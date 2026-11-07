# The Legend of Zelda: Ocarina of Time (0400486024DEC000): the rewriter's patches of this game's own builds. dm/tools/patch_nso.py loads every profile's patches.py and applies those of a
# module's FRAME_STEP as described there ("Registered patches"). Patches of Nintendo SDK module builds are in dm/tools/sdk_patches.py
from nso_asm import ADRP, B

# The game steps its world by its present interval. agl's display (vtable main+0x4c63f80, its frame method main+0x3b4ea90) runs an interval controller every frame (main+0x3b4ef60, on
# display +0x270: the bounds 1 and 3 at +0x0 / +0x4, the interval at +0x48 and its fps, 60 / interval, at +0x58); the controller applies the fps through setFrameRate (main+0x4dc0f0:
# interval 60 / fps to nvnWindowSetPresentInterval, main+0xf49970). The game's frame manager (main+0x6e6be0) steps its world by 60 / that fps every frame (main+0x6e6cc4) into the VFR
# object (main+0x3b4e300: +0x10 step, +0x14 its inverse, +0x1c 60 / step) and its game-frame counter (+0xd58); the pad's held-button counts take 60 / fps too (main+0x3b4eaf8 into the
# global the pad reads at main+0x348377c). The game fixes the interval at 1 (main+0x3372370 sets the controller's fixed bit, +0x60, and calls its setInterval, main+0x3b4f370, with 1),
# so the controller never measures, and at 30 fps the world moves at half speed. The stub at the controller's first instruction after its prologue sets the host's step instead: the
# interval and its level (+0x48 / +0x4c), fps 60 / step (+0x58 / +0x5c), the hysteresis counters cleared (+0x50 / +0x54), then takes the controller's own apply path (main+0x3b4f074,
# with x20 = the controller and x19 = the display as there), which presents at that interval; the manager then steps the world by the step. Without a target fps or before the host has
# decided a step, the original instruction runs. The VRR controller (main+0x4dbda0, taken when the display reports variable refresh rate) is not stubbed: the host reports none
def frame_step(ctx):
    here, emit, fs_site, fs_put, FS_STATE_OFF = ctx.here, ctx.emit, ctx.site, ctx.put, ctx.state
    fs_site(0x3b4ef84, '08804139')                                      # ldrb w8,[x0,#0x60]   the fixed bit
    start = here(); emit(ADRP(16, here(), FS_STATE_OFF))
    for w in (0xb9400211,   # ldr w17,[x16]          target fps (0 = off)
              0x340001d1,   # cbz w17,orig (+14)
              0xb9402211,   # ldr w17,[x16,#0x20]    step in vsyncs
              0x34000191,   # cbz w17,orig (+12)     not decided yet
              0x29094411,   # stp w17,w17,[x0,#0x48] interval and its level
              0xf900281f,   # str xzr,[x0,#0x50]     hysteresis counters
              0x52800789,   # mov w9,#60
              0x1ad10929,   # udiv w9,w9,w17
              0x290b2409,   # stp w9,w9,[x0,#0x58]   fps = 60 / step: the manager steps the world by 60 / fps
              0xf9401a09,   # ldr x9,[x16,#0x30]
              0x8b314129,   # add x9,x9,w17,uxtw
              0xf9001a09,   # str x9,[x16,#0x30]     vsyncs stepped
              0xaa0103f3,   # mov x19,x1             the display, as the apply path takes it
              0xaa0003f4):  # mov x20,x0             the controller
        emit(w)
    emit(B(here(), 0x3b4f074))                                          # apply: setFrameRate(display, fps), then the display's interval
    emit(0x39418008)                                                    # orig: ldrb w8,[x0,#0x60]
    emit(B(here(), 0x3b4ef88))
    fs_put(0x3b4ef84, [B(0x3b4ef84, start)], "agl's interval controller: the host's step (state page target fps; 0 = the game's fixed interval)")

    # The dynamic resolution's GPU load. The GPU meter (main+0x5a8f0, each frame) takes the GPU time between two counter timestamps in microseconds and its load as a percent of
    # one 1/60 s frame (main+0x5aa54 loads 16666.67 from main+0x3e40ec8, which nothing else reads), and the resolution controller steps down above its palette's LoadThreshold (98,
    # the palette's defaults at main+0x11e0920) and up after IncreaseCounterMax (60) frames below it. Under a 30 fps target a frame has 33.3 ms, but the load stayed a percent of
    # 16.7 ms, so a 25 ms frame read 150% and the scene stayed at its floor (683x384 of 1536x864). The stub loads the frame time of the target instead, 1e6 / target fps (state page,
    # a float: 16666.67 at 60, 33333.33 at 30); without a target, the game's constant. The target, not the step decided per frame: a frame held longer because it was late must not
    # raise the budget, or a slow GPU would raise its own resolution
    fs_site(0x5aa54, '02c94ebd')                                        # ldr s2,[x8,#0xec8]   16666.67 (x8 = its page)
    start = here(); emit(ADRP(9, here(), FS_STATE_OFF))
    for w in (0xb9400129,   # ldr w9,[x9]            target fps (float bits; 0 = off)
              0x340000e9,   # cbz w9,orig (+7)
              0x1e270123,   # fmov s3,w9
              0x52848009,   # mov w9,#0x2400
              0x72a92e89,   # movk w9,#0x4974,lsl #16   1e6
              0x1e270122,   # fmov s2,w9
              0x1e231842):  # fdiv s2,s2,s3          the target's frame time in microseconds
        emit(w)
    emit(B(here(), 0x5aa58))
    emit(0xbd4ec902)                                                    # orig: ldr s2,[x8,#0xec8]
    emit(B(here(), 0x5aa58))
    fs_put(0x5aa54, [B(0x5aa54, start)], "GPU meter: the load is a percent of the target's frame time (state page target fps; 0 = the game's 1/60 s)")

FRAME_STEP = {'e0f3ccfaf50065ae4ea01eb5aeb13b1a': frame_step}

# How general each patch is and could be (dm/tools/docs_patches.py "Binding", listed in docs/agents/game-patches.md): what, its binding now, the loosest it could have (goal),
# purpose, why; blocked or kept: why the gap stays open (cannot close yet, or left open on purpose); checked: what was checked on game files (else a judgement)
BINDING = [
    {'what': '60 / 30 fps frame step (agl interval controller)', 'now': 'build', 'goal': 'engine', 'purpose': 'frame rate',
     'why': "agl's display interval controller, which the game's frame manager steps its world by; other agl games may share it",
     'blocked': 'frame-step stubs have no function-matched form yet'},
    {'what': "GPU meter's budget follows the target fps (dynamic resolution)", 'now': 'build', 'goal': 'engine', 'purpose': 'rendering',
     'why': "the game's own GPU meter divides by a literal 1/60 s; another build moves the literal and its load",
     'blocked': 'frame-step stubs have no function-matched form yet'},
]
