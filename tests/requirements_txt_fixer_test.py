import pytest

from pre_commit_hooks.requirements_txt_fixer import FAIL
from pre_commit_hooks.requirements_txt_fixer import fix_requirements_txt
from pre_commit_hooks.requirements_txt_fixer import PASS
from pre_commit_hooks.requirements_txt_fixer import Requirement


@pytest.mark.parametrize(
    ('input_s', 'expected_retval', 'output'),
    (
        (b'', PASS, b''),
        (b'\n', PASS, b'\n'),
        (b'foo\nbar\n', FAIL, b'bar\nfoo\n'),
        (b'bar\nfoo\n', PASS, b'bar\nfoo\n'),
        (b'#comment1\nfoo\n#comment2\nbar\n', FAIL, b'#comment2\nbar\n#comment1\nfoo\n'),
        (b'#comment1\nbar\n#comment2\nfoo\n', PASS, b'#comment1\nbar\n#comment2\nfoo\n'),
        (b'#comment\n\nfoo\nbar\n', FAIL, b'#comment\n\nbar\nfoo\n'),
        (b'#comment\n\nbar\nfoo\n', PASS, b'#comment\n\nbar\nfoo\n'),
        (b'\nfoo\nbar\n', FAIL, b'bar\n\nfoo\n'),
        (b'\nbar\nfoo\n', PASS, b'\nbar\nfoo\n'),
        (b'pyramid==1\npyramid-foo==2\n', PASS, b'pyramid==1\npyramid-foo==2\n'),
        (b'ocflib\nDjango\nPyMySQL\n', FAIL, b'Django\nocflib\nPyMySQL\n'),
        (
            b'-e git+ssh://git_url@tag#egg=ocflib\nDjango\nPyMySQL\n',
            FAIL,
            b'Django\n-e git+ssh://git_url@tag#egg=ocflib\nPyMySQL\n',
        ),
    ),
)
def test_integration(input_s, expected_retval, output, tmpdir):
    path = tmpdir.join('file.txt')
    path.write_binary(input_s)

    output_retval = fix_requirements_txt([path.strpath])

    assert path.read_binary() == output
    assert output_retval == expected_retval


def test_requirement_object():
    top_of_file = Requirement()
    top_of_file.comments.append('#foo')
    top_of_file.value = b'\n'

    requirement_foo = Requirement()
    requirement_foo.value = b'foo'

    requirement_bar = Requirement()
    requirement_bar.value = b'bar'

    # This may look redundant, but we need to test both foo.__lt__(bar) and
    # bar.__lt__(foo)
    assert requirement_foo > top_of_file
    assert top_of_file < requirement_foo
    assert requirement_foo > requirement_bar
    assert requirement_bar < requirement_foo
