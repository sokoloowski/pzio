import json

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from werkzeug.exceptions import abort
from datetime import datetime

from app.app import db
from app.models import Category, Offer, User
from flask_security import auth_required
from app.forms.offer import AddEditOfferForm

bp = Blueprint("bp_main", __name__)


# Here you can read about routing:
# https://flask.palletsprojects.com/en/2.2.x/api/#url-route-registrations
# https://hackersandslackers.com/flask-routes/


@bp.route('/')
def main_get():
    categories = db.session.query(Category).all()
    offers = db.session.query(Offer).order_by(Offer.created_at).limit(8).all()
    images = {}
    for o in offers:
        images[o.id] = json.loads(o.images)
    return render_template('main.jinja',
                           offers=offers,
                           categories=categories,
                           images=images)


@bp.route('/offer/<int:offer_id>')
def offer_get(offer_id):
    categories = db.session.query(Category).all()
    offer = db.session.query(Offer).filter_by(id=offer_id).one_or_none()
    if offer is None:
        abort(404)
    images = json.loads(offer.images)
    author = db.session.query(User).filter_by(id=offer.author).one_or_none()
    return render_template('offer/offer.jinja',
                           offer=offer,
                           categories=categories,
                           images=images,
                           author=author)

@bp.route('/offer/add')
@auth_required()
def offer_add():
    form = AddEditOfferForm()
    return render_template('offer/offer_add_edit.jinja', form=form, offer_id=None)

@bp.route('/offer/<int:offer_id>/edit')
@auth_required()
def offer_edit(offer_id):
    form = AddEditOfferForm()
    offer = db.session.query(Offer).filter_by(id=offer_id).one_or_none()
    if offer is None:
        abort(404)
    if offer.author != current_user.id:
        abort(401)
    form.title.data = offer.title
    form.description.data = offer.description
    form.price.data = offer.price
    return render_template('offer/offer_add_edit.jinja', form=form, offer_id=offer_id)

@bp.route('/user/profile')
@auth_required()
def user_profile_get():
    return render_template('user/user_profile.jinja')

@bp.route('/user/offers')
@auth_required()
def user_offers_get():
    offers = db.session.query(Offer).filter_by(author=current_user.id).all()
    return render_template('user/user_offers.jinja', offers=offers)

@bp.route('/user/settings')
@auth_required()
def user_settings_get():
    return render_template('user/user_settings.jinja')


@bp.route('/api/offer/<int:offer_id>/edit', methods=["PUT", "POST"])
@auth_required()
def offer_edit_api(offer_id):
    form = AddEditOfferForm()
    db.session.query(Offer).filter(Offer.id == offer_id, Offer.author == current_user.id).update(
        {
            'title': form.title.data,
            'description': form.description.data,
            'price': form.price.data
        }
    )
    db.session.commit()
    return redirect(url_for('bp_main.user_offers_get'))

@bp.route('/api/offer/add', methods=["POST"])
@auth_required()
def offer_add_api():
    form = AddEditOfferForm()
    offer = Offer(author=current_user.id,
                  description=form.description.data,
                  category=1,
                  title=form.title.data,
                  price=form.price.data,
                  is_used=False,
                  images='["1200px-RedCat_8727.jpg", "cat.webp"]')
    db.session.add(offer)   
    db.session.commit()
    return redirect(url_for('bp_main.user_offers_get'))

@bp.route('/api/offer/<int:offer_id>/delete', methods=['DELETE', 'POST'])
@auth_required()
def offer_delete(offer_id):
    offer = db.session.query(Offer).filter_by(id=offer_id).one_or_none()
    if offer is None:
        abort(404)
    if offer.author != current_user.id:
        abort(401)
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('bp_main.user_offers_get'))

# TODO settings PUT endpoint
