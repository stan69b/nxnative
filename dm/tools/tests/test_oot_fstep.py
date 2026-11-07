"""Execute Ocarina of Time's frame-step stubs (agl's interval controller, the GPU meter's frame time) on ARM64, without game files.

Optional dependency: unicorn. On macOS its JIT needs execution outside the sandbox.
"""
import importlib.util
from pathlib import Path
import struct
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import unicorn as uc
    from unicorn import arm64_const as arm
except ImportError:
    uc = arm = None

spec = importlib.util.spec_from_file_location('oot_patches', Path(__file__).resolve().parents[2] / 'games/0400486024DEC000/patches.py')
patch = importlib.util.module_from_spec(spec); spec.loader.exec_module(patch)

SITE, BACK, APPLY = 0x3b4ef84, 0x3b4ef88, 0x3b4f074
METER, METER_BACK, METER_CONST = 0x5aa54, 0x5aa58, 0x3e40ec8   # the GPU meter's load of 16666.67 (1/60 s in microseconds), the instruction after it


@unittest.skipIf(uc is None, 'optional ARM64 execution dependency: unicorn')
class IntervalController(unittest.TestCase):
    base, area, state, ctl, disp = 0x10000000, 0x3c50000, 0x14000000, 0x15000000, 0x15001000

    def setUp(self):
        self.u = uc.Uc(uc.UC_ARCH_ARM64, uc.UC_MODE_ARM)
        for a, n in ((self.base, 0x3c60000), (self.state, 0x4000), (self.ctl, 0x2000)):
            self.u.mem_map(a, n)
        self.cursor = self.area
        self.puts = []
        ctx = types.SimpleNamespace(here=lambda: self.cursor, emit=self.emit, site=lambda off, orig: None, put=self.put, state=self.state - self.base)
        patch.frame_step(ctx)
        self.assertEqual([p[0] for p in self.puts], [SITE, METER])
        # the controller as the game leaves it: bounds 1..3, interval 1 fixed, fps 60, counters set
        self.u.mem_write(self.ctl, struct.pack('<2I', 1, 3))
        self.u.mem_write(self.ctl + 0x48, struct.pack('<6I', 1, 1, 5, 4, 60, 60))
        self.u.mem_write(self.ctl + 0x60, bytes([1]))
        self.u.reg_write(arm.UC_ARM64_REG_X0, self.ctl)
        self.u.reg_write(arm.UC_ARM64_REG_X1, self.disp)

    def emit(self, w):
        self.u.mem_write(self.base + self.cursor, struct.pack('<I', w)); self.cursor += 4

    def put(self, off, words, why):
        self.puts.append((off, words, why))
        self.u.mem_write(self.base + off, struct.pack('<' + 'I' * len(words), *words))

    def run_site(self, target, step, stepped=0):
        self.u.mem_write(self.state, struct.pack('<f', target))
        self.u.mem_write(self.state + 0x20, struct.pack('<I', step))
        self.u.mem_write(self.state + 0x30, struct.pack('<Q', stepped))
        ends = []
        def stop(u, a, n, d): ends.append(a); u.emu_stop()
        hooks = [self.u.hook_add(uc.UC_HOOK_CODE, stop, begin=self.base + a, end=self.base + a) for a in (BACK, APPLY)]
        try: self.u.emu_start(self.base + SITE, self.base + BACK, count=100)
        finally:
            for h in hooks: self.u.hook_del(h)
        return (ends[0] if ends else self.u.reg_read(arm.UC_ARM64_REG_PC)) - self.base   # emu_start stops at BACK before its hook fires

    def words(self, off, n): return struct.unpack('<%dI' % n, self.u.mem_read(self.ctl + off, 4 * n))
    def stepped(self): return struct.unpack('<Q', self.u.mem_read(self.state + 0x30, 8))[0]

    def test_host_step_sets_interval_and_fps_and_applies(self):
        for step, fps in ((1, 60), (2, 30), (3, 20)):
            with self.subTest(step=step):
                self.assertEqual(self.run_site(60.0, step, stepped=100), APPLY)
                self.assertEqual(self.words(0x48, 6), (step, step, 0, 0, fps, fps))   # interval, its level, counters, fps for the frame manager
                self.assertEqual(self.stepped(), 100 + step)
                self.assertEqual(self.u.reg_read(arm.UC_ARM64_REG_X20), self.ctl)    # the apply path's registers
                self.assertEqual(self.u.reg_read(arm.UC_ARM64_REG_X19), self.disp)
                self.assertEqual(self.words(0, 2), (1, 3))                            # bounds untouched

    def test_no_target_or_no_step_runs_the_game_controller(self):
        for target, step in ((0.0, 2), (60.0, 0)):
            with self.subTest(target=target, step=step):
                self.assertEqual(self.run_site(target, step, stepped=7), BACK)
                self.assertEqual(self.u.reg_read(arm.UC_ARM64_REG_W8), 1)             # the original ldrb w8,[x0,#0x60]: the fixed bit
                self.assertEqual(self.words(0x48, 6), (1, 1, 5, 4, 60, 60))
                self.assertEqual(self.stepped(), 7)

    def test_site_branches_to_the_stub(self):
        off, words, why = self.puts[0]
        w = words[0]
        self.assertEqual(w >> 26, 0b000101)
        imm = w & 0x3ffffff
        self.assertEqual(off + (imm << 2), self.area)


@unittest.skipIf(uc is None, 'optional ARM64 execution dependency: unicorn')
class GpuMeterBudget(unittest.TestCase):
    """The GPU meter's load is a percent of the frame time of the host's target, not of a fixed 1/60 s"""
    base, area, state = 0x10000000, 0x3c50000, 0x14000000

    def setUp(self):
        self.u = uc.Uc(uc.UC_ARCH_ARM64, uc.UC_MODE_ARM)
        for a, n in ((self.base, 0x3c60000), (self.base + 0x3e40000, 0x1000), (self.state, 0x4000)):
            self.u.mem_map(a, n)
        self.cursor = self.area
        self.puts = {}
        ctx = types.SimpleNamespace(here=lambda: self.cursor, emit=self.emit, site=lambda off, orig: None, put=self.put, state=self.state - self.base)
        patch.frame_step(ctx)
        self.u.mem_write(self.base + METER_CONST, struct.pack('<f', 16666.666))

    def emit(self, w):
        self.u.mem_write(self.base + self.cursor, struct.pack('<I', w)); self.cursor += 4

    def put(self, off, words, why):
        self.puts[off] = words
        self.u.mem_write(self.base + off, struct.pack('<' + 'I' * len(words), *words))

    def budget(self, target):
        """s2 after the meter's load, as the game's code goes on with it at METER_BACK; x8 holds the constant's page, as the adrp before the site leaves it"""
        self.u.mem_write(self.state, struct.pack('<f', target))
        self.u.reg_write(arm.UC_ARM64_REG_X8, self.base + (METER_CONST & ~0xfff))
        self.u.reg_write(arm.UC_ARM64_REG_V2, 0)
        self.u.emu_start(self.base + METER, self.base + METER_BACK, count=40)
        self.assertEqual(self.u.reg_read(arm.UC_ARM64_REG_PC) - self.base, METER_BACK)
        self.assertEqual(self.u.reg_read(arm.UC_ARM64_REG_X8), self.base + (METER_CONST & ~0xfff))   # x8 is the game's again after the load
        return struct.unpack('<f', struct.pack('<I', self.u.reg_read(arm.UC_ARM64_REG_V2) & 0xffffffff))[0]

    def test_site_is_patched(self):
        self.assertIn(METER, self.puts)

    def test_target_frame_time(self):
        for target, us in ((60.0, 16666.666), (30.0, 33333.332)):
            with self.subTest(target=target):
                self.assertAlmostEqual(self.budget(target), us, places=2)

    def test_60_is_the_games_own_constant(self):
        self.assertEqual(struct.pack('<f', self.budget(60.0)), struct.pack('<f', 16666.666))

    def test_no_target_keeps_the_games_constant(self):
        self.assertAlmostEqual(self.budget(0.0), 16666.666, places=2)


if __name__ == '__main__':
    unittest.main()
