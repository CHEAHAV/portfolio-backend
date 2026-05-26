from icb.core.db import engine
from sqlalchemy.orm import DeclarativeBase
from icb.core.model import Base

from datetime import datetime
from fastapi.encoders import jsonable_encoder

from icb.api.branch.models import TBL_BRANCH
from icb.api.company.models import TBL_COMPANY
from icb.api.menu.models import TBL_MENU, TBL_MENU_ITEM, TBL_SUB_MENU
from icb.api.module.models import TBL_FORM_MODULE, TBL_MODULE, TBL_MODULE_ACCESSMENT_ITEM
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.api.user.models import TBL_USER, TBL_USER_LOCATION_ASSIGNMENT
from icb.core.db import db
import icb.core.lib as core_lib
# from core.security import get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

   
def generate_module():
    moduleList = __import__("main")
    CRUDAPI = getattr(moduleList, "CRUDAPI")
    cs = [cls for cls in CRUDAPI.registry]

    for c in cs:
        m_obj = db.query(TBL_MODULE).filter(TBL_MODULE.name == c.module).first()
        if m_obj:
            m_obj.url   = c.url
            m_obj.model = c.model.__name__
            db.add(m_obj)
            print('============>', c.module)
        else:
            module = TBL_MODULE(
                id           = c.module,
                name         = c.module,
                num_of_auth  = 0,
                url          = c.url,
                model        = c.model.__name__,
                list_view    = 'LBB',
                query_list   = 'LBB',
                branch_id    = 'HQ',
                company_id   = 'SYSTEM',
                re_is_public = True
            )
            print('------------>', c.module)
            db.add(module)

            fmodule = TBL_FORM_MODULE(
                id           = c.module,
                module_id    = c.module,
                num_of_auth  = 0,
                list_view    = 'LBB',
                query_list   = 'LBB',
                branch_id    = 'HQ',
                company_id   = 'SYSTEM',
                re_is_public = False
            )
            db.add(fmodule)
            

def generate_menu_item():
    m_obj = db.query(TBL_MODULE).all()
    for m in m_obj:
        menu_obj = db.query(TBL_MENU_ITEM).filter(TBL_MENU_ITEM.url==m.url).first()
        if not menu_obj:
            print('Adding menu item for module:', m.name)
            id = core_lib.get_module_id(db, 'MenuItem', 'SYSTEM')
            menu = TBL_MENU_ITEM(
                id           = id,
                type         = 'standard',
                label        = m.name,
                module_id    = m.id,
                url          = m.url,
                icon         = 'local-original-dashboard1 v-icon',
                branch_id    = 'HQ',
                company_id   = 'SYSTEM',
                re_is_public = False
            )
            db.add(menu)
            # db.commit()

def generate_menu():
    obj = db.query(TBL_MENU).filter(TBL_MENU.id=='1').first()
    if not obj:
        m_obj = TBL_MENU(
            id          = '1',
            description = 'Menu',
            ordering    = 1,
            branch_id   = 'HQ',
            company_id  = 'SYSTEM'
        )
        db.add(m_obj)

        mi_obj = db.query(TBL_MENU_ITEM).all()
        count = 0
        for mi in mi_obj:
            count = count + 1
            sm_obj = TBL_SUB_MENU(
                id         = f'{count}_1',
                parent_id  = m_obj.id,
                label      = mi.label,
                main_id    = '',
                module_id  = mi.module_id,
                icon       = mi.icon,
                url        = mi.icon,
                type       = mi.type,
                ordering   = 0,
                branch_id  = 'HQ',
                company_id = 'SYSTEM'
            )
            db.add(sm_obj)


def generate_form_module(company_id):
    am_obj = db.query(TBL_MODULE_ACCESSMENT_ITEM).\
        filter(TBL_MODULE_ACCESSMENT_ITEM.company_id).\
        all()
    if am_obj:
        for am in am_obj:
            obj = db.query(TBL_FORM_MODULE).filter(
                TBL_FORM_MODULE.module_id==am.module_id,
                TBL_FORM_MODULE.company_id==company_id,
            ).first()
            fmodule = TBL_FORM_MODULE(
                id               = am.module_id,
                module_id        = am.module_id,
                num_of_auth      = 0,
                id_type          = 'Sequencial',
                id_prefix        = '',
                id_index         = 0,
                id_date_format   = '%Y%m%d',
                id_serial_length = 6,
                id_prev_date     = datetime.utcnow().strftime('%Y-%m-%d'),
                list_view        = 'LBB',
                query_list       = 'LBB',
                branch_id        = 'HQ',
                company_id       = company_id,
                re_is_public     = False
            )
            db.add(fmodule)
    else:
        m_obj = db.query(TBL_MODULE).all()
        for m in m_obj:
            obj = db.query(TBL_FORM_MODULE).filter(
                TBL_FORM_MODULE.module_id==m.id,
                TBL_FORM_MODULE.company_id==company_id,
            ).first()
            if not obj:
                fmodule = TBL_FORM_MODULE(
                    id               = m.module_id,
                    module_id        = m.module_id,
                    num_of_auth      = 0,
                    id_type          = 'Sequencial',
                    id_prefix        = '',
                    id_index         = 0,
                    id_date_format   = '%Y%m%d',
                    id_serial_length = 6,
                    id_prev_date     = datetime.utcnow().strftime('%Y-%m-%d'),
                    list_view        = 'LBB',
                    query_list       = 'LBB',
                    branch_id        = 'HQ',
                    company_id       = company_id,
                    re_is_public     = False
                )
                db.add(fmodule)


def generate_admin_role():
    role_obj = db.query(TBL_ROLE).filter(TBL_ROLE.id=='ADMIN').first()
    if not role_obj:
        print('create role')
        role_obj = TBL_ROLE(
            id           = 'ADMIN',
            name         = 'Administrator',
            name_lc      = 'Administrator',
            description  = 'Administrator Role with all permissions',
            is_superuser = False,
            branch_id    = 'HQ',
            company_id   = 'SYSTEM',
            re_is_public = False
        )
        db.add(role_obj)

    module_obj = db.query(TBL_MODULE).all()
    count = 1
    for m in module_obj:
        role_permission_obj = db.query(TBL_ROLE_MODULE).filter(
            TBL_ROLE_MODULE.parent_id == 'ADMIN',
            TBL_ROLE_MODULE.module_id == m.id
        ).first()
        if not role_permission_obj:
            count = count + 1
            role_permission_obj = TBL_ROLE_MODULE(
                id           = f'{count}_ADMIN',
                parent_id    = 'ADMIN',
                module_id    = m.id,
                permission   = 'ALL',
                branch_id    = 'HQ',
                company_id   = 'SYSTEM',
                re_is_public = False
            )
            db.add(role_permission_obj)

    db.add(role_obj)
    # db.commit()

def create_company():
    print('create company=============')
    c_obj = db.query(TBL_COMPANY).filter(TBL_COMPANY.id=='SYSTEM').first()
    if not c_obj:
        obj = TBL_COMPANY(
            id                  = 'SYSTEM',
            name                = 'SYSTEM',
            name_lc             = 'SYSTEM',
            description         = 'SYSTEM',
            description_lc      = 'SYSTEM',
            logo                = '',
            banner              = '',
            phone               = '088888888',
            phone_2             = '088888888',
            telegram            = '088888888',
            email               = 'system@innotechsolution.com',
            website             = 'innotechsolution.com',
            facebook            = 'innotechsolution.com',
            youtube             = 'innotechsolution.com',
            country_id          = '01',
            province_id         = '0101',
            district_id         = '010101',
            commune_id          = '01010101',
            village_id          = '0101010101',
            street_no           = '01',
            house_no            = '01',
            lat_long            = '',
            registration_number = '',
            vat_tin             = '',
            is_group_holding    = False,
            parent_company_id   = '',
            branch_id           = 'HQ',
            company_id          = 'SYSTEM'
        )
        db.add(obj)
        print('create branch=============')

        b_obj = TBL_BRANCH(
            id           = 'HQ',
            name         = 'HQ',
            name_lc      = 'HQ',
            phone        = '088888888',
            email        = 'system@innotechsolution.com',
            manager_name = 'Manager Name',
            opening_date = datetime.utcnow().strftime('%Y-%m-%d'),
            country_id   = '01',
            province_id  = '0101',
            district_id  = '010101',
            commune_id   = '01010101',
            village_id   = '0101010101',
            street_no    = '01',
            house_no     = '01',
            lat_long     = '',
            image        = '',
            active       = True,
            open_hours   = '00:00:00',
            close_hours  = '00:00:00',
            account_id   = '',
            qr_image     = '',
            distance     = 1,
            branch_id    = 'HQ',
            company_id   = 'SYSTEM'
        )
        db.add(b_obj)

def create_user_and_role():
    print('create role=============')
    r_obj = TBL_ROLE(
        id           = 'SUPERUSER',
        name         = 'SUPERUSER',
        name_lc      = 'SUPERUSER',
        is_superuser = True,
        description  = 'Superuser',
        branch_id    = 'HQ',
        company_id   = 'SYSTEM'
    )
    db.add(r_obj)
    print('create user=============')
    u_obj = TBL_USER(
        id               = 'SUPERUSER',
        first_name       = 'SUPERUSER',
        last_name        = 'SUPERUSER',
        email            = 'SUPERUSER',
        username         = 'SuperUser',
        phone            = '088888888',
        password         = get_password_hash('1qaz!QAZ'),
        pin              = '',
        photo            = '',
        is_active        = True,
        notification     = True,
        two_factor       = False,
        language         = 'en',
        last_activity_at = None,
        attempt          = 0,
        branch_id        = 'HQ',
        company_id       = 'SYSTEM',
        store_id         = 'HS',
    )
    db.add(u_obj)
    print('create location=============')
    l_obj = TBL_USER_LOCATION_ASSIGNMENT(
        id                    = '1_SUPERUSER',
        user_id               = 'SUPERUSER',
        accessible_company_id = 'SYSTEM',
        accessible_branch_ids = 'HQ',
        default_branch_id     = 'HQ',
        default_store_id      = 'HS',
        store_id              = 'HS',
        role_id               = 'SUPERUSER',
        is_default            = True,
        branch_id             = 'HQ',
        company_id            = 'SYSTEM'
    )
    db.add(l_obj)

from sqlalchemy.orm import Session as SASession
from icb.core.db import engine
from icb.core.model import Base

# Create ONE session at module level
db = SASession(engine)

def run():
    try:
        Base.metadata.create_all(bind=engine)
        db.rollback()
        create_company()
        create_user_and_role()
        generate_module()
        generate_menu_item()
        generate_admin_role()
        db.commit()
        print('Done! All data committed.')
    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
        raise

'''
# python
#> from migrations.generate_module import *
#> run()
#> db.commit()
'''    