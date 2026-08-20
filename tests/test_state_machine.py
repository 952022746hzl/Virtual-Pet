import random

from pet.state_machine import ONESHOT, SLEEP_AFTER, PetBrain, State


def make_brain(seed=1):
    return PetBrain(rng=random.Random(seed))


def tick(brain, seconds, dt=0.1):
    t = 0.0
    while t < seconds:
        brain.update(dt)
        t += dt


def test_sleeps_after_idle_timeout_and_wakes_on_click():
    brain = make_brain()
    tick(brain, SLEEP_AFTER + 1)
    assert brain.state is State.SLEEP
    brain.on_click()
    assert brain.state is State.IDLE
    assert ("say", "wake") in brain.pop_events()


def test_click_triggers_bow_with_quote_then_returns_to_idle():
    brain = make_brain()
    brain.on_click()
    assert brain.state is State.BOW
    assert ("say", "click") in brain.pop_events()
    tick(brain, ONESHOT[State.BOW] + 0.2)
    assert brain.state is State.IDLE


def test_drag_then_release_falls_then_hard_landing_says_ouch():
    brain = make_brain()
    brain.on_drag_start()
    assert brain.state is State.DRAGGED
    brain.on_drag_end()
    assert brain.state is State.FALL
    brain.on_land(hard=True)
    assert brain.state is State.LAND
    assert ("say", "land_hard") in brain.pop_events()
    brain2 = make_brain()
    brain2.on_drag_start(); brain2.on_drag_end()
    brain2.on_land(hard=False)
    assert brain2.state is State.IDLE


def test_interaction_resets_sleep_timer():
    brain = make_brain()
    tick(brain, SLEEP_AFTER - 1)
    brain.on_click()          # 互动重置计时
    tick(brain, ONESHOT[State.BOW] + 2)
    assert brain.state is not State.SLEEP


def test_idle_walk_alternates_eventually():
    brain = make_brain()
    seen = set()
    for _ in range(600):      # 60 秒足以掷出两种状态
        brain.update(0.1)
        seen.add(brain.state)
    assert {State.IDLE, State.WALK} <= seen


def test_coffee_flow():
    brain = make_brain()
    brain.command_coffee()
    assert brain.state is State.COFFEE
    brain.on_coffee_arrived()
    assert brain.state is State.BOW
    assert ("say", "coffee") in brain.pop_events()


def test_special_emits_scene_quote():
    brain = make_brain()
    brain.command_special("cancel_overtime")
    assert brain.state is State.SPECIAL
    assert ("say", "cancel_overtime") in brain.pop_events()


def test_chase_toggle():
    brain = make_brain()
    brain.set_chase(True)
    brain.set_chasing(True)
    assert brain.state is State.CHASE
    brain.set_chase(False)
    assert brain.state is State.IDLE


def test_ground_lost_starts_fall_unless_dragged():
    brain = make_brain()
    brain.on_ground_lost()
    assert brain.state is State.FALL
    brain2 = make_brain()
    brain2.on_drag_start()
    brain2.on_ground_lost()
    assert brain2.state is State.DRAGGED
