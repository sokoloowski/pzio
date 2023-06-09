from flask import url_for
from flask_admin.menu import MenuLink

from app import models
from app.views.admin.dormitory import DormitoryModelView
from app.views.admin.offer import OfferModelView
from app.views.admin.role import RoleModelView
from app.views.admin.user import UserModelView


def admin_panel_init(app, admin, db):
    class LogoutLink(MenuLink):
        def get_url(self):
            return url_for("security.logout")

    admin.add_link(LogoutLink(name="Wyloguj się"))

    admin.add_view(UserModelView(models.User, db.session, app=app, db=db, name='Użytkownicy'))
    admin.add_view(RoleModelView(models.Role, db.session, app=app, db=db, name='Role'))
    admin.add_view(OfferModelView(models.Offer, db.session, app=app, db=db, name='Ogłoszenia'))
    admin.add_view(DormitoryModelView(models.Dormitory, db.session, app=app, db=db, name='Akademiki'))
    admin.add_view(DormitoryModelView(models.Faculty, db.session, app=app, db=db, name='Wydziały'))
