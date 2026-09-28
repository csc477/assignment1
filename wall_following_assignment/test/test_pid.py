import importlib.util
import os

import pytest

HERE = os.path.dirname(__file__)
_spec = importlib.util.spec_from_file_location(
    'wall_follower', os.path.join(HERE, '..', 'scripts', 'wall_follower.py'))
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)


def test_proportional_term():
    pid = wf.PID(2.0, 0.0, 0.0, 0.1)
    pid.update_control(0.5)
    assert pid.get_control() == pytest.approx(1.0)


def test_derivative_term():
    pid = wf.PID(0.0, 1.0, 0.0, 0.5)
    pid.update_control(1.0)  # derivative = (1.0 - 0.0) / 0.5
    assert pid.get_control() == pytest.approx(2.0)


def test_integral_accumulates():
    pid = wf.PID(0.0, 0.0, 1.0, 0.1)
    pid.update_control(1.0)
    pid.update_control(1.0)
    assert pid.get_control() == pytest.approx(2.0)


def test_gains_are_plain_attributes():
    # the parameter callback mutates gains live
    pid = wf.PID(0.1, 0.0, 0.0, 0.1)
    pid.Kp = 1.0
    pid.update_control(0.5)
    assert pid.get_control() == pytest.approx(0.5)
