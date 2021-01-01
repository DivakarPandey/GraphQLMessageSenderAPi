# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView

# initializing our app
app = Flask(__name__)
app.debug = True

# Configs
# Replace the user, password, hostname and database according to your configuration information
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Divakar@1@localhost:5432/MessageSender'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Modules
db = SQLAlchemy(app)


# Models
class User(db.Model):
    __tablename__ = 'users'

    phonenumber = db.Column(db.Text, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    messages = db.relationship('SendMessage', backref='author')

    def __init__(self, phonenumber, username):
        self.phonenumber = phonenumber
        self.username = username

    def __repr__(self):
        return '<User %r>' %self.phonenumber


class SendMessage(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    phonenumber = db.Column(db.Text,  db.ForeignKey('users.phonenumber'))

    def __repr__(self):
        return '<SendMessage %r>' %self.phonenumber %self.message %self.date


# Schema Objects
class SendMessageObject(SQLAlchemyObjectType):
    class Meta:
        model = SendMessage
        interfaces = (graphene.relay.Node,)


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_messages = SQLAlchemyConnectionField(SendMessageObject)
    all_users = SQLAlchemyConnectionField(UserObject)

schema = graphene.Schema(query=Query)


#mutations

#mutation to add new  message from existing user phonenumber
class AddMessage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        phonenumber = graphene.String(required=True)
        message = graphene.String(required=True)
        date = graphene.String(required=True)

    message = graphene.Field(lambda: SendMessageObject)

    def mutate(self, info,id,phonenumber,message,date):
        message = SendMessage(id=id,phonenumber=phonenumber,message=message,date=date)
        db.session.add(message)
        db.session.commit()
        return AddMessage(message=message)

#mutation to add new user in database
class AddUser(graphene.Mutation):
    class Arguments:
        phonenumber = graphene.String(required=True)
        username = graphene.String(required=True)

    user = graphene.Field(lambda: UserObject)

    def mutate(self, info, phonenumber, username):
        user = User(phonenumber=phonenumber,username=username)
        db.session.add(user)
        db.session.commit()
        return AddUser(user=user)



class Mutation(graphene.ObjectType):
    add_user = AddUser.Field()
    add_message = AddMessage.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)

# Routes
app.add_url_rule(
    '/graphql-api',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)


@app.route('/')
def index():
    return '<h1>Welcome to message sender  Api</h1>'


if __name__ == '__main__':
    app.run()
