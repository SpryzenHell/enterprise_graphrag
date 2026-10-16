from __future__ import annotations

from scripts.train_mixed_corpus_guard import select_training_window_bounds


def _paired_sequences(position: str):
    context = list(range(1000))
    attack = list(range(-30, 0))
    if position == "start":
        poisoned = attack + context
        attack_start, attack_end = 0, len(attack)
    elif position == "middle":
        attack_start = len(context) // 2
        poisoned = context[:attack_start] + attack + context[attack_start:]
        attack_end = attack_start + len(attack)
    else:
        attack_start = len(context)
        poisoned = context + attack
        attack_end = attack_start + len(attack)

    pos_start, pos_length = select_training_window_bounds(
        token_count=len(poisoned),
        content_limit=510,
        position=position,
        is_poisoned=True,
        attack_start=attack_start,
        attack_end=attack_end,
        attack_length=len(attack),
        paired_attack=True,
    )
    clean_start, clean_length = select_training_window_bounds(
        token_count=len(context),
        content_limit=510,
        position=position,
        is_poisoned=False,
        attack_length=len(attack),
        paired_attack=True,
    )
    positive_window = poisoned[pos_start:pos_start + pos_length]
    clean_window = context[clean_start:clean_start + clean_length]
    return context, attack, positive_window, clean_window, attack_start - pos_start


def test_start_position_pairs_keep_identical_source_context_window():
    context, attack, positive_window, clean_window, local_attack_start = _paired_sequences("start")

    assert local_attack_start == 0
    assert positive_window[:len(attack)] == attack
    assert positive_window[len(attack):] == clean_window
    assert clean_window == context[:480]


def test_middle_position_pairs_keep_identical_context_around_attack():
    context, attack, positive_window, clean_window, local_attack_start = _paired_sequences("middle")

    left_context = local_attack_start
    right_context_start = local_attack_start + len(attack)
    assert positive_window[left_context:right_context_start] == attack
    context_without_attack = positive_window[:left_context] + positive_window[right_context_start:]
    assert context_without_attack == clean_window
    assert clean_window == context[260:740]


def test_end_position_pairs_keep_identical_source_context_window():
    context, attack, positive_window, clean_window, local_attack_start = _paired_sequences("end")

    assert positive_window[local_attack_start:] == attack
    assert positive_window[:local_attack_start] == clean_window
    assert clean_window == context[520:1000]


def test_non_bipia_documents_keep_full_candidate_window_budget():
    start, length = select_training_window_bounds(
        token_count=1000,
        content_limit=510,
        position="end",
        is_poisoned=False,
        attack_length=0,
        paired_attack=False,
    )
    assert (start, length) == (490, 510)
