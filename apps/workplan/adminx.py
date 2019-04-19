# -*- coding: utf-8 -*-
from .models import CdnLog,OperationLog

import xadmin



xadmin.site.register(CdnLog)
xadmin.site.register(OperationLog)