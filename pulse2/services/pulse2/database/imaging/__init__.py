# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Database class for imaging
"""

from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.database.imaging.types import *

from sqlalchemy import *
from sqlalchemy.sql import union
from sqlalchemy.orm import *

import logging

DATABASEVERSION = 1

class ImagingDatabase(DyngroupDatabaseHelper):
    """
    Class to query the Pulse2 imaging database.

    DyngroupDatabaseHelper is a Singleton, so is ImagingDatabase
    """


    def db_check(self):
        self.my_name = "ImagingDatabase"
        self.configfile = "imaging.ini"
        return DyngroupDatabaseHelper.db_check(self, DATABASEVERSION)

    def activate(self, config):
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("ImagingDatabase don't need activation")
            return None
        self.logger.info("ImagingDatabase is activating")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, convert_unicode=True)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        self.nomenclatures = {'LogState':LogState, 'TargetType':TargetType}
        self.fk_nomenclatures = {'Log':{'fk_log_state':'LogState'}, 'Target':{'type':'TargetType'}}
        self.__loadNomenclatureTables()
        self.is_activated = True
        self.dbversion = self.getImagingDatabaseVersion()
        self.logger.debug("ImagingDatabase finish activation")
        return self.db_check()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the imaging database
        """
        self.version = Table("version", self.metadata, autoload = True)
        
        self.initTables()
        mapper(BootService, self.boot_service)
        mapper(BootServiceInMenu, self.boot_service_in_menu)
        mapper(BootServiceOnImagingServer, self.boot_service_on_imaging_server)
        mapper(Entity, self.entity)
        mapper(Image, self.image)
        mapper(ImageInMenu, self.image_in_menu)
        mapper(ImageOnImagingServer, self.image_on_imaging_server)
        mapper(ImagingServer, self.imaging_server)
        mapper(Internationalization, self.internationalization)
        mapper(Language, self.language)
        mapper(Log, self.log)
        mapper(LogState, self.log_state)
        mapper(Menu, self.menu, properties = { 'default_item':relation(MenuItem), 'default_item_WOL':relation(MenuItem) } )
        mapper(MenuItem, self.menu_item, properties = { 'menu' : relation(Menu) })
        mapper(Partition, self.partition)
        mapper(PostInstallScript, self.post_install_script)
        mapper(PostInstallScriptInImage, self.post_install_script_in_image)
        mapper(Protocol, self.protocol)
        mapper(Target, self.target)
        mapper(TargetType, self.target_type)
        mapper(User, self.user)


    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """

        self.boot_service = Table(
            "BootService",
            self.metadata,
            autoload = True
        )

        self.boot_service_in_menu = Table(
            "BootServiceInMenu",
            self.metadata,
            Column('fk_bootservice', Integer, ForeignKey('BootService.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            autoload = True
        )

        self.boot_service_on_imaging_server = Table(
            "BootServiceOnImagingServer",
            self.metadata,
            Column('fk_boot_service', Integer, ForeignKey('BootService.id'), primary_key=True),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            autoload = True
        )

        self.entity = Table(
            "Entity",
            self.metadata,
            autoload = True
        )

        self.image = Table(
            "Image",
            self.metadata,
            Column('fk_creator', Integer, ForeignKey('User.id')),
            autoload = True
        )

        self.image_in_menu = Table(
            "ImageInMenu",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            autoload = True
        )

        self.image_on_imaging_server = Table(
            "ImageOnImagingServer",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            autoload = True
        )

        self.imaging_server = Table(
            "ImagingServer",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            autoload = True
        )

        self.internationalization = Table(
            "Internationalization",
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('fk_language', Integer, ForeignKey('Language.id'), primary_key=True),
            autoload = True
        )

        self.language = Table(
            "Language",
            self.metadata,
            autoload = True
        )

        self.log = Table(
            "Log",
            self.metadata,
            Column('fk_log_state', Integer, ForeignKey('LogState.id')),
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_target', Integer, ForeignKey('Target.id')),
            autoload = True
        )

        self.log_state = Table(
            "LogState",
            self.metadata,
            autoload = True
        )

        self.menu = Table(
            "Menu",
            self.metadata,
            # cant put them for circular dependancies reasons, the join must be explicit
            # Column('fk_default_item', Integer, ForeignKey('MenuItem.id')), 
            # Column('fk_default_item_WOL', Integer, ForeignKey('MenuItem.id')),
            Column('fk_protocol', Integer, ForeignKey('Protocol.id')),
            # fk_name is not an explicit FK, you need to choose the lang before beeing able to join
            autoload = True
        )

        self.menu_item = Table(
            "MenuItem",
            self.metadata,
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
            # fk_name is not an explicit FK, you need to choose the lang before beeing able to join
            autoload = True
        )

        self.partition = Table(
            "Partition",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id')),
            autoload = True
        )

        self.post_install_script = Table(
            "PostInstallScript",
            self.metadata,
            autoload = True
        )

        self.post_install_script_in_image = Table(
            "PostInstallScriptInImage",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_post_install_script', Integer, ForeignKey('PostInstallScript.id'), primary_key=True),
            autoload = True
        )

        self.protocol = Table(
            "Protocol",
            self.metadata,
            autoload = True
        )

        self.target = Table(
            "Target",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
            autoload = True
        )

        self.target_type = Table(
            "TargetType",
            self.metadata,
            autoload = True
        )

        self.user = Table(
            "User",
            self.metadata,
            autoload = True
        )

    def __loadNomenclatureTables(self):
        session = create_session()
        for i in self.nomenclatures:
            n = session.query(self.nomenclatures[i]).all()
            self.nomenclatures[i] = {}
            for j in n:
                self.nomenclatures[i][j.id] = j.label
        session.close()

    def completeNomenclatureLabel(self, objs):
        if type(objs) != list and type(objs) != tuple:
            objs = [objs]
        if len(objs) == 0:
            return
        className = str(objs[0].__class__).split("'")[1].split('.')[-1]
        nomenclatures = []
        if self.fk_nomenclatures.has_key(className):
            for i in self.fk_nomenclatures[className]:
                nomenclatures.append([i, i.replace('fk_', ''), self.nomenclatures[self.fk_nomenclatures[className][i]]])
            for obj in objs:
                for fk, field, value in nomenclatures:
                    if fk == field:
                        setattr(obj, '%s_value'%field, value[getattr(obj, fk)])
                    else:
                        setattr(obj, field, value[getattr(obj, fk)])

    def completeTarget(self, objs):
        """
        take a list of dict with a fk_target element and add them the target dict that correspond
        """
        ids = {}
        for i in objs:
            ids[i['fk_target']] = None
        ids = ids.keys()
        targets = self.__getTargetById(ids)
        id_target = {}
        for t in targets:
            t = t.toH()
            id_target[t['id']] = t
        for i in objs:
            i['target'] = id_target[i['fk_target']]

    def getImagingDatabaseVersion(self):
        """
        Return the imaging database version.
        We don't use this information for now, but if we can get it this means the database connection is working.

        @rtype: int
        """
        return self.version.select().execute().fetchone()[0]

###########################################################
    def __getTargetById(self, ids):
        session = create_session()
        n = session.query(Target).filter(self.target.c.id.in_(ids)).all()
        session.close()
        return n

    def __mergeTargetInLog(self, log_list):
        ret = []
        for log, target in log_list:
            setattr(log, 'target', target)
            ret.append(log)
        return ret

    def __getTargetsMenuQuery(self, session):
        return session.query(Menu).select_from(self.menu.join(self.target))
        
    def getTargetsMenuTID(self, target_id):
        session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.id == target_id).first() # there should always be only one!
        session.close()
        return q
        
    def getTargetsMenuTUUID(self, target_id, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.uuid == target_id).first() # there should always be only one!
        if need_to_close_session:
            session.close()
        return q
    
    def __mergeMenuItemInBootService(self, list_of_bs, list_of_both):
        ret = []
        temporary = {}
        for bs, mi in list_of_both:
            if mi != None:
                temporary[bs.id] = mi
        for bs, bs_id in list_of_bs:
            if temporary.has_key(bs_id):
                setattr(bs, 'menu_item', temporary[bs_id])
            ret.append(bs)
        return ret
    
    def __mergeBootServiceInMenuItem(self, my_list):
        ret = []
        for mi, bs, menu in my_list:
            if bs != None:
                setattr(mi, 'boot_service', bs)
            if menu != None:
                setattr(mi, 'default', (menu.fk_default_item == mi.id))
                setattr(mi, 'default_WOL', (menu.fk_default_item_WOL == mi.id))
            ret.append(mi)
        return ret
    
    def __mergeMenuItemInImage(self, list_of_im, list_of_both):
        ret = []
        temporary = {}
        for im, mi in list_of_both:
            if mi != None:
                temporary[im.id] = mi
        for im, im_id in list_of_im:
            if temporary.has_key(im_id):
                setattr(im, 'menu_item', temporary[im_id])
            ret.append(im)
        return ret
    def __mergeBootServiceOrImageInMenuItem(self, mis):
        """ warning this one does not work on a list but on a tuple of 3 elements (mi, bs, im) """
        (menuitem, bootservice, image, menu) = mis
        if bootservice != None:
            setattr(menuitem, 'boot_service', bootservice)
        if image != None:
            setattr(menuitem, 'image', image)
        if menu != None:
            setattr(menuitem, 'default', (menu.fk_default_item == menuitem.id))
            setattr(menuitem, 'default_WOL', (menu.fk_default_item_WOL == menuitem.id))
        return menuitem
 
    def __mergeImageInMenuItem(self, my_list):
        ret = []
        for mi, im, menu in my_list:
            if im != None:
                setattr(mi, 'image', im)
            if menu != None:
                setattr(mi, 'default', (menu.fk_default_item == mi.id))
                setattr(mi, 'default_WOL', (menu.fk_default_item_WOL == mi.id))
            ret.append(mi)
        return ret

    def getMenuContent(self, menu_id, type = MENU_ALL, start = 0, end = -1, filter = ''):# TODO implement the start/end with a union betwen q1 and q2
        session = create_session()

        mi_ids = session.query(MenuItem).add_column(self.menu_item.c.id).select_from(self.menu_item.join(self.menu))
        if filter != '':
            mi_ids = mi_ids.filter(and_(self.menu.c.id == menu_id, self.menu_item.c.desc.like('%'+filter+'%')))
        else:
            mi_ids = mi_ids.filter(self.menu.c.id == menu_id)
        mi_ids = mi_ids.order_by(self.menu_item.c.order)
        if end != -1:
            mi_ids = mi_ids.offset(int(start)).limit(int(end)-int(start))
        else:
            mi_ids = mi_ids.all()
        mi_ids = map(lambda x:x[1], mi_ids)
        
        q = []
        if type == MENU_ALL or type == MENU_BOOTSERVICE:
            q1 = session.query(MenuItem).add_entity(BootService).add_entity(Menu).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu))
            q1 = q1.filter(self.menu_item.c.id.in_(mi_ids)).order_by(self.menu_item.c.order).all()
            q1 = self.__mergeBootServiceInMenuItem(q1)
            q.extend(q1)
        if type == MENU_ALL or type == MENU_IMAGE:
            q2 = session.query(MenuItem).add_entity(Image).add_entity(Menu).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu))
            q2 = q2.filter(self.menu_item.c.id.in_(mi_ids)).order_by(self.menu_item.c.order).all()
            q1 = self.__mergeImageInMenuItem(q2)
            q.extend(q2)
        session.close()
        q.sort(lambda x,y: cmp(x.order, y.order))
        return q
        
    def countMenuContentFast(self, menu_id): # get MENU_ALL and empty filter
        session = create_session()
        q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).count()
        session.close()
        return q
        
    def countMenuContent(self, menu_id, type = MENU_ALL, filter = ''):
        if type == MENU_ALL and filter =='':
            return self.countMenuContentFast(menu_id)
        
        session = create_session()
        q = 0
        if type == MENU_ALL or type == MENU_BOOTSERVICE:
            q1 = session.query(MenuItem).add_entity(BootService).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service))
            q1 = q1.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.desc.like('%'+filter+'%'))).count()
            q += q1
        if type == MENU_ALL or type == MENU_IMAGE:
            q2 = session.query(MenuItem).add_entity(Image).select_from(self.menu_item.join(self.image_in_menu).join(self.image))
            q2 = q2.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.desc.like('%'+filter+'%'))).count()
            q += q2
        session.close()
        return q
         
###########################################################
    def getEntityUrl(self, location_uuid):
        session = create_session()
        # there should be just one imaging server per entity
        q = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity)).filter(self.entity.c.uuid == location_uuid).first() 
        session.close()
        if q == None:
            return None
        return q.url
    
    def __Logs4Location(self, session, location_uuid, filter):
        n = session.query(Log).add_entity(Target).select_from(self.log.join(self.target).join(self.entity)).filter(self.entity.c.uuid == location_uuid)
        if filter != '':
            n = n.filter(or_(self.log.c.title.like('%'+filter+'%'), self.target.c.name.like('%'+filter+'%')))
        return n
        
    def getLogs4Location(self, location_uuid, start, end, filter):
        session = create_session()
        n = self.__Logs4Location(session, location_uuid, filter)
        if end != -1:
            n = n.offset(int(start)).limit(int(end)-int(start))
        else:
            n = n.all()
        session.close()
        n = self.__mergeTargetInLog(n)
        return n

    def countLogs4Location(self, location_uuid, filter):
        session = create_session()
        n = self.__Logs4Location(session, location_uuid, filter)
        n = n.count()
        session.close()
        return n
    
    #####################
    def __LogsOnTargetByIdAndType(self, session, target_id, type, filter):
        q = session.query(Log).add_entity(Target).select_from(self.log.join(self.target)).filter(or_(self.target.c.id == target_id, self.target.c.uuid == target_id))
        if type == TYPE_COMPUTER:
            q = q.filter(self.target.c.type == 1)
        elif type == TYPE_PROFILE:
            q = q.filter(self.target.c.type == 2)
        else:
            self.logger.error("type %s does not exists!"%(type))
            # to be sure we dont get anything, this is an error case!
            q = q.filter(self.target.c.type == 0)
        if filter != '':
            q = q.filter(or_(self.log.c.title.like('%'+filter+'%'), self.target.c.name.like('%'+filter+'%')))
        return q
        
    def getLogsOnTargetByIdAndType(self, target_id, type, start, end, filter):
        session = create_session()
        q = self.__LogsOnTargetByIdAndType(session, target_id, type, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end)-int(start))
        else:
            q = q.all()
        session.close()
        q = self.__mergeTargetInLog(q)
        return q
    
    def countLogsOnTargetByIdAndType(self, target_id, type, filter):
        session = create_session()
        q = self.__LogsOnTargetByIdAndType(session, target_id, type, filter)
        q = q.count()
        session.close()
        return q
    
    ######################
    def __PossibleBootServices(self, session, target_uuid, filter):
        q = session.query(BootService).add_column(self.boot_service.c.id)
        q = q.select_from(self.boot_service.join(self.boot_service_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target))
        q = q.filter(self.target.c.uuid == target_uuid)
        if filter != '':
            q = q.filter(or_(self.boot_service.c.desc.like('%'+filter+'%'), self.boot_service.c.value.like('%'+filter+'%')))
        return q

    def __PossibleBootServiceAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(BootService).add_entity(MenuItem)
        q = q.filter(and_(
            self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            self.menu_item.c.fk_menu == menu_id,
            self.boot_service.c.id.in_(bs_ids)
        )).all()
        return q
   
    def getPossibleBootServices(self, target_uuid, start, end, filter):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleBootServices(session, target_uuid, filter)
        q1 = q1.group_by(self.boot_service.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu.id)
        session.close()
        
        q = self.__mergeMenuItemInBootService(q1, q2)
        return q

    def countPossibleBootServices(self, target_uuid, filter):
        session = create_session()
        q = self.__PossibleBootServices(session, target_uuid, filter)
        q = q.count()
        session.close()
        return q

    ERR_TARGET_HAS_NO_MENU = 1000
    def addServiceToTarget(self, bs_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice'%(ERR_TARGET_HAS_NO_MENU)
            
        mi = MenuItem()
        mi.default_name = params['name']
        mi.hidden = params['hidden']
        mi.hidden_WOL = params['hidden_WOL']
        # put it at the last position
        mi.order = self.countMenuContentFast(menu.id) + 1
        mi.desc = bs.desc
        mi.fk_name = 0 # TODO i18n in internationalize!
        mi.fk_menu = menu.id
        session.save(mi)
        session.flush()
        
        is_menu_modified = False
        if params['default']:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if is_menu_modified:
            session.save_or_update(menu)

        bsim = BootServiceInMenu()
        bsim.fk_menuitem = mi.id
        bsim.fk_bootservice = uuid2id(bs_uuid)
        session.save(bsim)
        session.flush()
                
        session.close()
        return None
    
    def editServiceToTarget(self, bs_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice'%(ERR_TARGET_HAS_NO_MENU)

        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()

        mi.default_name = params['default_name']
        mi.hidden = params['hidden']
        mi.hidden_WOL = params['hidden_WOL']
        if params.has_key('order'):
            mi.order = params['order'] # TODO put the order!
        mi.desc = bs.desc
        mi.fk_name = 0 # TODO i18n in internationalize!
        mi.fk_menu = menu.id
        session.save_or_update(mi)
        session.flush()

        is_menu_modified = False
        if menu.fk_default_item != mi.id and params['default']:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if menu.fk_default_item == mi.id and not params['default']:
            is_menu_modified = True
            menu.fk_default_item = None
            
        if menu.fk_default_item_WOL != mi.id and params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if menu.fk_default_item_WOL == mi.id and not params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = None

        if is_menu_modified:
            session.save_or_update(menu)

        session.flush()
        session.close()
        return None

    def delServiceToTarget(self, bs_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        bsim = session.query(BootServiceInMenu).select_from(self.boot_service_in_menu.join(self.menu_item).join(self.boot_service).join(self.menu).join(self.target))
        bsim = bsim.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        session.delete(mi)
        session.delete(bsim)
        session.flush()

        session.close()
        return None

    def getMenuItemByUUID(self, mi_uuid):
        session = create_session()
        mi = session.query(MenuItem).add_entity(BootService).add_entity(Image).add_entity(Menu)
        mi = mi.select_from(self.menu_item.join(self.menu).outerjoin(self.boot_service_in_menu).outerjoin(self.boot_service).outerjoin(self.image_in_menu).outerjoin(self.image))
        mi = mi.filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()
        mi = self.__mergeBootServiceOrImageInMenuItem(mi)
        session.close()
        return mi
    
    ######################
    def __PossibleImages(self, session, target_uuid, filter):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target))
        q = q.filter(self.target.c.uuid == target_uuid, or_(self.image.c.is_master == True, and_(self.image.c.is_master == False, )))
        if filter != '':
            q = q.filter(or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.value.like('%'+filter+'%')))
        return q

    def __PossibleImageAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(Image).add_entity(MenuItem)
        q = q.filter(and_(
            self.image_in_menu.c.fk_bootservice == self.image.c.id,
            self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
            self.menu_item.c.fk_menu == menu_id,
            self.image.c.id.in_(bs_ids)
        )).all()
        return q
   
    def getPossibleImages(self, target_uuid, start, end, filter):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleImages(session, target_uuid, filter)
        q1 = q1.group_by(self.image.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)
        session.close()
        
        q = self.__mergeMenuItemInImage(q1, q2)
        return q

    def countPossibleImages(self, target_uuid, filter):
        session = create_session()
        q = self.__PossibleImages(session, target_uuid, filter)
        q = q.count()
        session.close()
        return q
        
    ######################
    def getBootServicesOnTargetById(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, MENU_BOOTSERVICE, start, end, filter)
        return menu_items

    def countBootServicesOnTargetById(self, target_id, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, MENU_BOOTSERVICE, filter)
        return count_items

    ######################
    def getBootMenu(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, MENU_ALL, start, end, filter)
        return menu_items
        
    def countBootMenu(self, target_id, filter): 
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, MENU_ALL, filter)
        return count_items

def id2uuid(id):
    return "UUID%d" % id
def uuid2id(uuid):
    return uuid.replace("UUID", "")

###########################################################
class DBObject(object):
    to_be_exported = ['id', 'name', 'label']
    need_iteration = []
    def getUUID(self):
        return id2uuid(self.id)
    def to_h(self):
        return self.toH()
    def toH(self, level = 0):
        ImagingDatabase().completeNomenclatureLabel(self)
        ret = {}
        for i in dir(self):
            if i in self.to_be_exported:
                ret[i] = getattr(self, i)
            if i in self.need_iteration and level < 1:
                # we dont want to enter in an infinite loop 
                # and generaly we dont need more levels
                ret[i] = getattr(self, i).toH(level+1)
        if not ret.has_key('uuid'):
            ret['imaging_uuid'] = self.getUUID()
        return ret

class BootService(DBObject):
    to_be_exported = ['id', 'value', 'desc', 'uri']
    need_iteration = ['menu_item']

class BootServiceInMenu(DBObject):
    pass

class BootServiceOnImagingServer(DBObject):
    pass

class Entity(DBObject):
    to_be_exported = ['id', 'name', 'uuid']

class Image(DBObject):
    to_be_exported = ['id', 'path', 'checksum', 'size', 'desc', 'is_master', 'creation_date', 'fk_creator']

class ImageInMenu(DBObject):
    pass

class ImageOnImagingServer(DBObject):
    pass

class ImagingServer(DBObject):
    to_be_exported = ['id', 'name', 'url', 'packageserver_uuid', 'recursive', 'fk_entity']

class Internationalization(DBObject):
    to_be_exported = ['id', 'label', 'fk_language']

class Language(DBObject):
    to_be_exported = ['id', 'label']

class Log(DBObject):
    to_be_exported = ['id', 'timestamp', 'title', 'completeness', 'detail', 'fk_log_state', 'fk_image', 'fk_target', 'log_state', 'image']
    need_iteration = ['target']

class LogState(DBObject):
    to_be_exported = ['id', 'label']

class Menu(DBObject):
    to_be_exported = ['id', 'default_name', 'fk_name', 'timeout', 'background_uri', 'message', 'fk_default_item', 'fk_default_item_WOL', 'fk_protocol']

class MenuItem(DBObject):
    to_be_exported = ['id', 'default_name', 'order', 'hidden', 'hidden_WOL', 'fk_menu', 'fk_name', 'default', 'default_WOL', 'desc']
    need_iteration = ['boot_service', 'image']

class Partition(DBObject):
    to_be_exported = ['id', 'filesystem', 'size', 'fk_image']

class PostInstallScript(DBObject):
    to_be_exported = ['id', 'name', 'value', 'uri']

class PostInstallScriptInImage(DBObject):
    pass

class Protocol(DBObject):
    to_be_exported = ['id', 'label']

class Target(DBObject):
    to_be_exported = ['id', 'name', 'uuid', 'type', 'fk_entity', 'fk_menu']

class TargetType(DBObject):
    to_be_exported = ['id', 'label']

class User(DBObject):
    to_be_exported = ['id', 'login']

