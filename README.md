# Getup Controller

This is an initial work to move all logic from getup-api into kubernetes-aware components.

## Available components so far:

### Project Reconciler

Watch for namespaces/projects with annotation `getup.io/owner` and creates a corresponding
`Project` instance in getup-api.

Next components:

### Resources Reconciler

Sync limits/requests from getup-api into namespaces.

## Installing

To build the image locally:

```
$ make image
```


Build and push to registry:

```
$ make release
```

Use make vars to overwrite defaults:

```
$ make release VERSION=v0.0.1 REPOSITORY=getupcloud IMAGE_NAME=getup-controller
```

Deploy the app into kubernetes.

```
## Set a value to deployment envs GETUP_API_USERNAME and GETUP_API_PASSWORD
$ vim templates/controller.yaml

$ kubectl apply -f templates/
```
