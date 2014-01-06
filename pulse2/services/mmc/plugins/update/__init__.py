# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
"""
Update plugin for the MMC agent
"""
import logging
import time
import os
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger()

from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.core.tasks import TaskManager
from mmc.plugins.update.config import updateConfig
from mmc.plugins.update.database import updateDatabase
from mmc.plugins.msc import create_update_command
from pulse2.managers.group import ComputerGroupManager

VERSION = "0.0.0"
APIVERSION = "0:1:0"
REVISION = ""

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION


def activate():
    config = updateConfig("update")
    if config.disabled:
        logger.warning("Plugin UpdateMgr: disabled by configuration.")
        return False
    if not updateDatabase().activate(config):
        logger.error("UpdateMgr database not activated")
        return False
    return True

def calldb(func, *args, **kw):
    return getattr(updateDatabase(), func).__call__(*args, **kw)

def get_os_classes(params):
    return updateDatabase().get_os_classes(params)

def get_update_types(params):
    return updateDatabase().get_update_types(params)

def get_updates(params):
    return updateDatabase().get_updates(params)

def set_update_status(update_id, status):
    return updateDatabase().set_update_status(update_id, status)

def create_update_commands():
    # TODO: ensure that this method is called by taskmanager
    # and not directly by XMLRPC
    
    # Creating root context
    ctx = SecurityContext()
    ctx.userid = 'root'
    
    # Get all enabled os_classes
    os_classes = updateDatabase().get_os_classes({'filters': {'enabled' : 1}})
    
    # Create update command for enabled os_classes
    for os_class in os_classes['data']:
        # Get all OS dyngroup machines
        dyngroup_name = 'PULSE_INTERNAL_UPDATE_GROUP||' + os_class['name']
        targets = ComputerGroupManager().result_group_by_name(ctx, dyngroup_name)
        
        # Fetching all targets
        for uuid in targets:
            machine_id = int(uuid.lower().replace('uuid', ''))
            updates = updateDatabase().get_eligible_updates_for_host(machine_id)
            
            update_list = [update['uuid'] for update in updates]
            
            # Create update command for this host with update_list
            create_update_command(ctx, [uuid], update_list)
    return True

