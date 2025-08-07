# Copyright 2025 RTLMeter contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
from functools import cached_property
from typing import Any, Dict, Final, List, final

from rtlmeter import yaml_descriptor

###############################################################################
# All global state in the program are contained in the singleton Context object
###############################################################################


@final
class Context:
    # Verbose mode enable
    verbose: bool

    def __init__(self) -> None:
        self.verbose = False

    # Absolute path to root of repository
    @cached_property
    def rootDir(self) -> str:
        value = os.environ["RTLMETER_ROOT"]
        assert os.path.isabs(value), (
            "RTLMETER_ROOT must be set to the absolute path to the root of RTLMeter"
        )
        return value

    # Default working directory
    @cached_property
    def defaultWorkDir(self) -> str:
        return "work"

    # YAML descriptors as loaded from disk, indexed by design name
    @cached_property
    def descriptors(self) -> Dict[str, Dict[str, Any]]:
        designsDir = os.path.join(self.rootDir, "designs")
        value = {}
        for design in sorted(os.listdir(designsDir)):
            designDir = os.path.join(designsDir, design)
            fileName = os.path.join(designDir, "descriptor.yaml")
            if descr := yaml_descriptor.load(fileName):
                value[design] = descr
                value[design]["__file__"] = fileName
                value[design]["designDir"] = designDir
        return value

    # All available cases
    @cached_property
    def availableCases(self) -> List[str]:
        value = []
        for designName, desc in self.descriptors.items():
            rootTests = set(desc["execute"]["tests"].keys())
            for configName, config in desc["configurations"].items():
                configTests = set(config["execute"]["tests"].keys())
                for testName in rootTests | configTests:
                    value.append(f"{designName}:{configName}:{testName}")
        return sorted(value)

    # CPUs usable by this process
    @cached_property
    def usableCpus(self) -> List[int]:
        return sorted(_ for _ in os.sched_getaffinity(0))


CTX: Final[Context] = Context()
