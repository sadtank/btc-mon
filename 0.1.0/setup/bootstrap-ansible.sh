#!/usr/bin/env bash
set -e

USER_TO_USE="${USER_TO_USE:-${SUDO_USER:-${USER}}}"
#echo "$USER_TO_USE"

# Determine directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running as root (sudo)
if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run with sudo or as root."
  echo "Try: sudo $0 $*"
  exit 1
fi

# Install Ansible
echo "Installing Ansible..."
sudo apt-get install -y ansible || { echo "Failed to install Ansible"; exit 1; }

# Ensure the playbook exists
if [ ! -f "$SCRIPT_DIR/playbook.yml" ]; then
  echo "Playbook not found at $SCRIPT_DIR/playbook.yml"
  exit 1
fi

# Run Ansible playbook
echo "Running Ansible playbook..."
ansible-playbook "$SCRIPT_DIR/playbook.yml" -vv || { echo "Ansible playbook failed"; exit 1; }

echo "Script completed successfully."
