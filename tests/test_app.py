r"""
To test a lightning app:
1. Use LightningTestApp which is a subclass of LightningApp.
2. Subclass run_once in LightningTestApp.
3. in run_once, come up with a way to verify the behavior you wanted.

run_once runs your app through one cycle of the event loop and then terminates
"""
import io
import os
from contextlib import redirect_stdout

from lightning.testing.testing import application_testing, LightningTestApp



class LightningAppTestInt(LightningTestApp):
    def run_once(self) -> bool:
        f = io.StringIO()
        with redirect_stdout(f):
            super().run_once()
        out = f.getvalue()
        assert "⚡ Lightning HackerNews App! ⚡\n" == out
        return True


@mock.patch.dict(os.environ, {"LAI_TEST": "True"}, clear=True)
def test_hackernews_app():
    cwd = os.getcwd()
    cwd = os.path.join(cwd, "app.py")
    command_line = [
        cwd,
        "--blocking",
        "False",
        "--open-ui",
        "False",
    ]
    result = application_testing(LightningAppTestInt, command_line)
    assert result.exit_code == 0
