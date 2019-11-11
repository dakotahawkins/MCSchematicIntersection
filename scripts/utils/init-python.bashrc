[[ -f /etc/bash.bashrc ]] && source /etc/bash.bashrc
[[ -f ~/.bashrc ]] && source ~/.bashrc

export INSIDE_INIT_PYTHON=1

init_python_set_PS1() {
    local old_extglob=$(shopt -p extglob)
    shopt -s extglob

    local old_PS1="$PS1"
    export PS1=${PS1/%\$*([^\$])/[venv] \$ }
    [[ "$PS1" = "$old_PS1" ]] && export PS1="$PS1 [venv] "

    eval "$old_extglob"
}
init_python_set_PS1
unset -f init_python_set_PS1
