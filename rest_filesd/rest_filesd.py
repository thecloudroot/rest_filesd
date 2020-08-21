"""
    PROMETHEUS REST SD
"""

from flask import Flask, jsonify, make_response, render_template
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from yaml import Loader, load
from .models import db
from .models import Job, Target, Label
from .log import logger
from .utils import generate_targets_yaml

### Application logic
SWAGGER_URL = '/api'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # API url
#swagger_yml = load(open(swagger_path, 'r'), Loader=Loader)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
      # Swagger UI static files mapped to {SWAGGER_URL}/dist
    API_URL,
    # Swagger UI config overrides
    config={
        'app_name':"REST file service discovery",
        'info':{"title":"REST API"},
        'title':"REST API"
    }
    #oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #   'clientId': "your-client-id",
    #   'clientSecret': "your-client-secret-if-required",
    #   'realm': "your-realms",
    #   'appName': "your-app-name",
    #   'scopeSeparator': " ",
    #   'additionalQueryStringParams': {'test': "hello"}
    #}
)



def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.update(dict(
        TESTING = True
    ))
    # app.config.from_object(config_object)
    # app.config.from_object()
    # app.config.from_object(config[config_name])

    # app.config.update(dict(
    #     PORT = 4449
    # #os.path.join(app.root_path, 'flaskr.db'),
    # #     DEBUG=True,
    # #     SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
    # #     USERNAME='marto',
    # #     PASSWORD='marto'
    # ))
    # app.config.update(config or {})
    # app.config.from_envvar('FLASKR_SETTINGS', silent=True)

    # Connect to database (and create file if it doesn't exists
    db.connect(reuse_if_open=True)

    #    logging.info("DB engine is {}".format(current_app.config.DATABASE))

    if not Target.table_exists() or not Job.table_exists() or not Label.table_exists():
        init_db(db)

    # Register routes and error pages
    register_blueprints(app)
    register_error_pages(app)

    sample_data(db)

    # Generate YAML files from latest data in DB
    generate_targets_yaml()

    #@app.route("/spec")
    #def spec():
    #    return jsonify(swagger(app))
    # Start the app
    # app.run(debug=True, port=int(config.PORT))
    # app.run(debug=False, port=4999)
#    @app.route('/')
#    def index():
#        return "Prometheus service discovery"
#    @app.route("/spec")
#    def spec():
#        return jsonify(swagger(app))

# Create a URL route in our application for "/"
    @app.route('/')
    def home():
        """
        This function just responds to the browser ULR
        localhost:5000/

        :return:        the rendered template 'home.html'
        """
        return render_template('home.html')

    @app.route('/index')
    def index():
        """
        This function just responds to the browser ULR
        localhost:5000/

        :return:        the rendered template 'home.html'
        """
        return render_template('index.html')



    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "0.0.7"
        swag['info']['title'] = "Prometheus REST API"
        return jsonify(swag)

    return app

def register_blueprints(app):
    """ Register all blueprint modules """

    from .views import target_blueprint
    app.register_blueprint(target_blueprint)

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def register_error_pages(app):
    # Register global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        response = jsonify({'message': error.description})
        response.status_code = 400
        return response

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': error.description}), 404)

    @app.errorhandler(409)
    def conflict(error):
        response = jsonify({'message': error.description})
        response.status_code = 409
        return response

    @app.errorhandler(422)
    def conflict(error):
        response = jsonify({'message': error.description})
        response.status_code = 422
        return response

def init_db(db):
    db.create_tables([Target, Job, Label])

def sample_data(db):
    # Create tables
    db.drop_tables([Target, Job, Label])
    db.create_tables([Target, Job, Label])

    # Create sample jobs, targets and labels
    sample_jobs = [{"name": "bug_me_not", "port": "9110"},
                   {"name": "blackbox", "port": ""},
                   {"name": "blackbox1", "port": ""}]
    for sample in sample_jobs:
        Job.create(name=sample['name'], port=sample['port'])
        # print("Created job %s" % sample['name'])

    sample_targets = [{"host": "cola1.example.com", "job": "blackbox"},
                      {"host": "cola2.example.com", "job": "blackbox1"}]
    for sample in sample_targets:
        Target.create(host=sample['host'], job=Job.select().where(Job.name == sample['job']).get())
        # print("Created target %s" % sample['host'])

    sample_labels = [{"label": "environment", "value": "enterprise", "host": "cola1.example.com"},
                     {"label": "severity", "value": "CRITICAL", "host": "cola2.example.com"}]
    for sample in sample_labels:
        Label.create(label=sample['label'], value=sample['value'],
                     target=Target.select().where(Target.host == sample['host']).get())
        # print("Created label %s for target %s" % (sample['label'], sample['host']))

    logger.debug("Created sample data.")
