from flask import jsonify, request
from flask_login import login_required

from redash.handlers.api import api
from redash.handlers.base import routes
from redash.models import Group, Organization, db
from redash.monitor import get_status
from redash.permissions import require_super_admin
from redash.security import talisman


@routes.route('/ping', methods=['GET'])
@talisman(force_https=False)
def ping():
    return 'PONG.'


@routes.route('/status.json')
@login_required
@require_super_admin
def status_api():
    status = get_status()
    return jsonify(status)


@routes.route('/api/organizations/create', methods=['POST'])
@login_required
@require_super_admin
def create_organization():
    req = request.get_json(True)
    name = req['name']
    slug = req['slug']

    org = Organization(name=name, slug=slug, settings={})
    admin_group = Group(name='admin', permissions=['admin', 'super_admin'], org=org, type=Group.BUILTIN_GROUP)
    default_group = Group(name='default', permissions=Group.DEFAULT_PERMISSIONS, org=org, type=Group.BUILTIN_GROUP)

    db.session.add_all([org, admin_group, default_group])
    db.session.commit()

    return jsonify({'created': True})


def init_app(app):
    from redash.handlers import embed, queries, static, authentication, admin, setup, organization
    app.register_blueprint(routes)
    api.init_app(app)
