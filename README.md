# Gubbi Gaem

## Docker Compose:

```yaml
services:
    gubbi-gaem:
        container_name: gubbi-gaem
        environment:
            - OPENAI_API_KEY=
        ports:
            - 8000:8000
        image: ghcr.io/mangocoder360/gubbi-gaem:latest
```