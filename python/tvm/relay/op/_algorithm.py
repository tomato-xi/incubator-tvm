# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"Definition of classic algorithms"
# pylint: disable=invalid-name,unused-argument
from __future__ import absolute_import

from tvm.te.hybrid import script
from tvm.runtime import convert
from topi.util import get_const_int, get_const_tuple
from . import strategy
from . import op as _reg
from .op import OpPattern, register_pattern
from .op import register_strategy

# argsort
register_strategy("argsort", strategy.argsort_strategy)
register_pattern("argsort", OpPattern.OPAQUE)

# topk
register_strategy("topk", strategy.topk_strategy)
register_pattern("topk", OpPattern.OPAQUE)

@script
def _topk_shape_func(data, k, axis):
    ndim = len(data.shape)
    val_out = output_tensor((ndim,), "int64")
    indices_out = output_tensor((ndim,), "int64")

    for i in const_range(ndim):
        if i != axis:
           val_out[i] = int64(data.shape[i])
           indices_out[i] = int64(data.shape[i])
        else:
            if k[0] < 1:
                val_out[i] = int64(data.shape[i])
                indices_out[i] = int64(data.shape[i])
            else:
                val_out[i] = int64(k[0])
                indices_out[i] = int64(k[0])
    return val_out, indices_out

@_reg.register_shape_func("topk", True)
def topk_shape_func(attrs, inputs, _):
    return [*_topk_shape_func(inputs[0], inputs[1], convert(attrs.axis))]

