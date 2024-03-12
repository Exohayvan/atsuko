# Build

### This is mostly just some info for me when building :>


Watchtower to keep docker image up to date.
```
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 300
```