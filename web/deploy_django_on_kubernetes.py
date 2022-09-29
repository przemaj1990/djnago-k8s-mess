
# Create VENV for work:
# https://www.youtube.com/watch?v=NAOsLaB6Lfc
# -----
from turtle import down


python3.9 -V
docker --version
kubectl version --client
mkdir -p Dev/django-k8s
cd Dev/django-k8s
# will create venv dir and put everything there
python3.9 -m venv venv 
source venv/bin/activate
# pip free show what is installed:
pip freeze
python -V
pip install pip --upgrade
touch requirements.txt
# Django start project:
mkdir web
cd web
django-admin startproject django_k8s .
code .
# next vork with VS code to have seperate work space & add workspace file
cd web
touch .env
touch .gitignore
#setup git
git init
git add --all
git commit -m 'initial commit'
# -----
# setup dotenv in wsgi.py & manage.py
# -----
# prepare Dockerfile (https://www.youtube.com/watch?v=NAOsLaB6Lfc&t=2849s):
#   find docker image: https://hub.docker.com/_/python/tags?page=1&name=3.9.13-slim
#   .dockignore - will tell Dockerfile what file should be ignored when COPY
#   run virtual venv in docker: RUN python3 -m venv /opt/venv
#   to activate virtual venv in dockerfile: CMD ["/app/entrypoint.sh"] & create file entrypoint.sh
#   we can run /Users/przemyslawmajdanski/Documents/DevOps/DeployDjango/Dev/django-k8s/venv/bin/gunicorn django_k8s.wsgi:application 
# -----
# solve problem with python manage.py makemigrations (https://www.youtube.com/watch?v=NAOsLaB6Lfc&t=3673s)
# -----
# Docker-Compose:
# https://github.com/codingforentrepreneurs/Django-Kubernetes/blob/main/docker-compose.yaml 
docker-compose up
docker-compose down
django-k8s % docker-compose up --build  # <- force build
# problem with: /app/django_k8s/wsgi.py:24: UserWarning: Not reading /app/.env - it doesn't exist (finally i dont solved this and this is not necessary)
#   https://stackoverflow.com/questions/67839672/docker-compose-up-gets-stuck-at-env-doesnt-exist
#   https://raturi.in/blog/manage-django-environments-secrets-using-python-decouple/
# copy specific commit from git:
git clone <repository>
git reset --hard <COMMIT-SHA-ID>
# problem with connection to databse: https://stackoverflow.com/questions/37307346/is-the-server-running-on-host-localhost-1-and-accepting-tcp-ip-connections
docker-compose up -d # -d run command in detach mode / in backgroud
docker system prune --all --force --volumes # remove a lot!
psql -p 5434 -h localhost -U myuser dockerdc # to log on posgresql
# there was no creation of superuser as we commit part of docker-compose where was run script that create super user
# kubernetes:
~/.kube/config  #<- location of config files to get access to cluster
kubectl --kubeconfig c1-cp1-kubernetes.yaml get nodes #<- using kubconfig file to access kubernetes cluster and get output from command
echo $KUBECONFIG # or echo $Env:KUBECONFIG
export KUBECONFIG=/Users/przemyslawmajdanski/Documents/DevOps/DeployDjango/Dev/django-k8s/web/c1-cp1-kubernetes.yaml
kubectl get nodes 
kubectl apply -f k8s/nginx/deployment.yaml
kubectl get pods
kubectl get deployments
kubectl describe deployments
kubectl describe deployments nginx-deployment
kubectl exec -it <podname> -- /bin/bash
kubectl exec -it nginx-deployment-684c85b7f4-q6wfs -- /bin/bash
kubectl delete -f k8s/nginx/deployment.yaml 
kubectl apply -f k8s/nginx/service.yaml
kubectl get service
kubectl get service nginx-service -o yaml > testfile.yaml
curl -i <ip_external>
kubectl apply -f k8s/nginx/service.yaml
kubectl get services
kubectl get service --all-namespaces
# problem with pending external ip in service: https://medium.com/swlh/kubernetes-external-ip-service-type-5e5e9ad62fcd
kubectl delete -f k8s/nginx/service.yaml 
kubectl delete -f k8s/nginx/deployment.yaml 
# https://github.com/codingforentrepreneurs/iac-python <- iac-python
kubectl apply -f k8s/nginx/apps/iac-python.yaml
kubectl exec -it iac-python-deployment-5658967669-8s96b -- /bin/bash
# privision private container registry" (best to have some private container trgistry)
docker compose up --build
docker login <external registry address> # or you can use just dokcer login and use docker hub
docker build -t przemaj1990/django-k8s:v1 -f Dockerfile .
docker images
docker push przemaj1990/django-k8s:v1
# on movie he integrate image wirh Kubernetes at 2:43 of movie. 
https://hub.docker.com/repository/docker/przemaj1990/django-k8s/tags?page=1&ordering=last_updated #<- pushed images
# next he setup posgresql on digitalocean
# how to copy database from pre-existing one:
PGPASSWORD=hasło pg_restore -U username -h databse_addres.com -p 25060 -d databse_name <local_pg_dump_path>
# next:
python -c "import secrets;print(secrets.token_urlsafe(32))" # generate secrete for superuser password in .env
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' # generate secrete key for .env
# create secrete: 
kubectl create secret generic django-k8s-web-prod-env --from-env-file=.env
kubectl get secrets
kubectl get secrets django-k8s-web-prod-env -o yaml #<- to see secret, but it will be encrypted
kubectl delete secrets django-k8s-web-prod-env # if you would liek to change .env, just delete secrete and create it again, 
# we can use this secrete in deploy yaml, prepare secrete to connect to dockerhub:
kubectl create secret docker-registry regcred --docker-username=przemaj1990 --docker-password=Mugin1234 --docker-email=przemaj1990@gmail.com
kubectl get serviceaccount default -o YAML
kubectl get secrets regcred -o yaml
# and use this secrete in imagePullSecrets in deploy file(https://stackoverflow.com/questions/49032812/how-to-pull-image-from-dockerhub-in-kubernetes)
kubectl get pods -w # show how containers are created
docker build -t przemaj1990/django-k8s:v1.2 -f Dockerfile .
docker push przemaj1990/django-k8s:v1.2
# https://hub.docker.com/repository/docker/przemaj1990/django-k8s
kubectl exec -it django-k8s-web-deployment-65c5fcb49d-4scd2 -- /bin/bash
source /opt/venv/bin/activate
python manage.py migrate #to check if db is working
python manage.py shell
import os
print(os.environ.get("DJANGO_SUPERUSER_USERNAME")) #to print env variable and check if they was used here
# if we change .env we need to delete nad create again secrete and recreate deployment
kubectl logs django-k8s-web-deployment-65c5fcb49d-4scd2
docker build -t przemaj1990/django-k8s:v1.3 -f Dockerfile .
docker push przemaj1990/django-k8s:v1.3
kubectl get pods
# -------
# Work on Posgresql to connect with django:
# start with: https://markgituma.medium.com/kubernetes-local-to-production-with-django-3-postgres-with-migrations-on-minikube-31f2baa8926e
kubectl apply -f k8s/nginx/apps/posgresql.yaml
kubectl get pv
kubectl get pvc

