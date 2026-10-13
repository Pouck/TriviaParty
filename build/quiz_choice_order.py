"""Mix named answer choices, keeping A-D labels and the answer key aligned."""
import hashlib
import random

def randomize_choices(questions, package_id, extra_positions=()):
    # Balanced positions, in shuffled order; deterministic builds remain reviewable.
    rng = random.Random(int.from_bytes(hashlib.sha256(package_id.encode()).digest()[:8], 'big'))
    positions = list(range(4)) * (len(questions) // 4) + list(extra_positions)
    assert len(positions) == len(questions)
    rng.shuffle(positions)
    for question, target in zip(questions, positions):
        assert question['kind'] == 'multipleChoice' and not question.get('randomVariants')
        assert len(question['options']) == 4
        names = [option.split(' — ', 1)[1] for option in question['options']]
        assert len(set(names)) == 4
        answer = names[question['correctOptionIndex']]
        distractors = [name for index, name in enumerate(names) if index != question['correctOptionIndex']]
        rng.shuffle(distractors)
        distractors.insert(target, answer)
        question['options'] = [f'{letter} — {name}' for letter, name in zip('ABCD', distractors)]
        question['correctOptionIndex'] = target
        assert question['options'][target].split(' — ', 1)[1] == answer
