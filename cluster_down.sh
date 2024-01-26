#!/bin/bash

# shellcheck disable=SC2162
read -p "Are you sure you want to execute 'docker-compose down -v'? (y/N): " choice

case "$choice" in
  y|Y )
    echo "Cluster down..."
    docker-compose down -v
    ;;
  n|N )
    echo "Operation aborted."
    ;;
  * )
    echo "Invalid choice. Please enter 'y' or 'n'."
    ;;
esac
