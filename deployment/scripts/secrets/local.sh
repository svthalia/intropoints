#!/bin/bash

######################
# Superuser creation #
######################

# creates a django super user
#
# !! the backend container must be running in order
# !! to call this function
#
# $1 -> username
# $2 -> e-mail
# $3 -> password
create_django_super_user() {
  echo "Checking if admin user '$1' already exists..."

  local user_exists
  user_exists=$(docker exec -i backend bash -c "
      python manage.py shell -c \"
  from django.contrib.auth import get_user_model;
  User = get_user_model();
  print(User.objects.filter(username='$1').exists())
  \" 2>/dev/null | tr -d '\r\n '
    ")

  if [ "$user_exists" = "True" ]; then
    echo "Admin user '$1' already exists. Skipping creation..."
    return
  fi

  # otherwise, just create the admin user
  echo "Creating admin..."
  docker exec -it backend bash -c "
  export DJANGO_SUPERUSER_PASSWORD='$3' && \
  python manage.py createsuperuser \
    --no-input \
    --username '$1' \
    --email '$2'
  "
}

################
# App creation #
################

# adds a local oauth application for the frontend to
# redirect to
#
# $1 -> OAuth client id
# $2 -> OAuth client secret
add_local_oauth_app() {
  echo "Adding local application..."
  docker exec -i backend python manage.py shell -c "
from oauth2_provider.models import Application;
from django.contrib.auth import get_user_model;
user = get_user_model().objects.filter(is_superuser=True).first();
app = Application.objects.update_or_create(
    name='frontend',
    client_id='$1',
    client_secret='$2',
    redirect_uris='$PROTOCOL_CHOICE://$DOMAIN_NAME/auth/callback/',
    user=user,
    client_type='public',
    authorization_grant_type='implicit',
    skip_authorization=True
);" > /dev/null
}
