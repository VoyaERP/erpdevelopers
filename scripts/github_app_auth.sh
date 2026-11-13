#!/usr/bin/env bash
# Source this function INSIDE the install/update subshell.
# Tokens are minted by ~/.config/erpdevelopers/github_app_credential.py on demand.
erpdev_enable_github_app_git() {
  local helper="${ERPDEV_GHAPP_HELPER:-$HOME/.config/erpdevelopers/github_app_credential.py}"
  test -r "$helper" || {
    echo "STOP: missing GitHub App helper at $helper" >&2
    return 2
  }
  command -v python3 >/dev/null || {
    echo "STOP: python3 required for GitHub App credential helper" >&2
    return 2
  }
  export GIT_CONFIG_COUNT=3
  export GIT_CONFIG_KEY_0=credential.helper
  export GIT_CONFIG_VALUE_0=
  export GIT_CONFIG_KEY_1=credential.helper
  export GIT_CONFIG_VALUE_1="!python3 \"$helper\""
  export GIT_CONFIG_KEY_2=credential.useHttpPath
  export GIT_CONFIG_VALUE_2=true
  export GIT_TERMINAL_PROMPT=0
}
