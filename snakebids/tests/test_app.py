from argparse import ArgumentParser
from os import PathLike
from configargparse import Namespace
from pytest_mock.plugin import MockerFixture
from ..app import SnakeBidsApp
from .mock.config import config
from unittest.mock import patch
import pytest
import sys, copy

def init_snakebids_app(self):
    self.configfile_path="mock/config.yaml"
    self.snakefile = "mock/Snakefile"
    self.config = copy.deepcopy(config)


class TestCreateParser:
    mock_args_special= ["--derivatives", "path/to/nowhere"]
    mock_basic_args = ["script_name", "path/to/input", "path/to/output", "participant"]
    mock_all_args = mock_basic_args + mock_args_special 

    @pytest.fixture
    def app(self, mocker: MockerFixture):
        mocker.patch.object(SnakeBidsApp, '__init__', init_snakebids_app)
        return SnakeBidsApp()

    @pytest.fixture
    def parser(self, app):
        return app._SnakeBidsApp__create_parser()

    def test_snakebids_app_is_properly_mocked(self, app):
        assert isinstance(app, SnakeBidsApp)
        assert not hasattr(app, "parser")

    def test_fails_if_missing_arguments(self, parser: ArgumentParser, mocker: MockerFixture):
        mocker.patch.object(sys, 'argv', ["script_name"])
        with pytest.raises(SystemExit):
            parser.parse_args()

    def test_succeeds_if_given_positional_args(self, parser: ArgumentParser, mocker: MockerFixture):
        mocker.patch.object(sys, 'argv', self.mock_basic_args)
        assert isinstance(parser.parse_args(), Namespace)

    def test_converts_type_path_into_pathlike(self, parser: ArgumentParser, mocker: MockerFixture):
        mocker.patch.object(sys, 'argv', self.mock_all_args)
        args = parser.parse_args()
        assert isinstance(getattr(args, "derivatives")[0], PathLike)
    
    def test_fails_if_undefined_type_given(self, app: SnakeBidsApp, mocker: MockerFixture):
        app.config["parse_args"]["--new-param"] = {
            "help": "Generic Help Message",
            "type": "UnheardClass"
        }
        with pytest.raises(TypeError):
            app._SnakeBidsApp__create_parser()
