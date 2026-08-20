from pet.physics import (
    GRAVITY,
    HARD_LANDING_SPEED,
    Body,
    Platform,
    step_fall,
    supporting_platform,
)

GROUND = Platform(left=0, right=1920, top=1040)


def test_gravity_accelerates_fall():
    body = Body(x=100, y=100)
    after, landed = step_fall(body, [GROUND], dt=0.033)
    assert landed is None
    assert after.y > body.y
    assert after.vy == GRAVITY * 0.033


def test_lands_on_platform_and_snaps():
    body = Body(x=100, y=1040 - 128 - 5, vy=600)  # 脚离地 5px，正在下落
    after, landed = step_fall(body, [GROUND], dt=0.033)
    assert landed == GROUND
    assert after.foot_y == GROUND.top


def test_lands_on_highest_crossed_platform():
    window_top = Platform(left=0, right=1920, top=500)
    lower_top = Platform(left=0, right=1920, top=530)
    body = Body(x=100, y=500 - 128 - 2, vy=1500)  # 一个 tick 扫掠区间 ≈[498, 550]，同时越过 500 和 530
    after, landed = step_fall(body, [GROUND, lower_top, window_top], dt=0.033)
    assert landed == window_top
    assert after.foot_y == window_top.top


def test_misses_platform_when_not_horizontally_over_it():
    narrow = Platform(left=500, right=700, top=500)
    body = Body(x=100, y=500 - 128 - 2, vy=1500)  # center_x=164，不在平台上方
    _, landed = step_fall(body, [narrow], dt=0.033)
    assert landed is None


def test_supporting_platform_detects_standing():
    body = Body(x=100, y=GROUND.top - 128)
    assert supporting_platform(body, [GROUND]) == GROUND
    assert supporting_platform(Body(x=100, y=100), [GROUND]) is None


def test_hard_landing_threshold_constant():
    assert 0 < HARD_LANDING_SPEED < 1800.0
