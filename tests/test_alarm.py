from alarm.manager import AlarmManager


def test_alarm_enter_exit_with_grace():
    am = AlarmManager(grace_seconds=3.0)
    # t=0: id1 enters zone
    am.update(ids_in_zone={1}, visible_ids={1}, now=0.0)
    assert am.is_on(1) is True
    # t=1: still in zone
    am.update(ids_in_zone={1}, visible_ids={1}, now=1.0)
    assert am.is_on(1) is True
    # t=2: exits zone but visible, countdown starts
    am.update(ids_in_zone=set(), visible_ids={1}, now=2.0)
    assert am.is_on(1) is True
    # t=4.9: still within 3s grace from t=2 -> alarm still on
    am.update(ids_in_zone=set(), visible_ids={1}, now=4.9)
    assert am.is_on(1) is True
    # t=5.1: grace elapsed -> alarm off
    am.update(ids_in_zone=set(), visible_ids={1}, now=5.1)
    assert am.is_on(1) is False


def test_alarm_reenter_cancels_timer():
    am = AlarmManager(grace_seconds=3.0)
    am.update(ids_in_zone={1}, visible_ids={1}, now=0.0)
    assert am.is_on(1) is True
    # Exit at t=1 -> start countdown to 4
    am.update(ids_in_zone=set(), visible_ids={1}, now=1.0)
    assert am.is_on(1) is True
    # Re-enter before deadline at t=2 -> cancel timer
    am.update(ids_in_zone={1}, visible_ids={1}, now=2.0)
    assert am.is_on(1) is True
    # Leave view entirely at t=2.5 -> start new countdown
    am.update(ids_in_zone=set(), visible_ids=set(), now=2.5)
    assert am.is_on(1) is True
    # Deadline would be 5.5
    am.update(ids_in_zone=set(), visible_ids=set(), now=5.6)
    assert am.is_on(1) is False
