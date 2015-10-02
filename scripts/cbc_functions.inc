if [[ -n $BASH_VERSION ]] && \
    [[ "$(basename "$0" 2> /dev/null)" == "cbc_functions.inc" ]]; then
        echo "$(basename "$0") is designed to be sourced not executed."
        exit 1 
fi
function success {
    echo $?
}; export -f success

function program_exists {
    PROGRAM="$1"
    which $PROGRAM &>/dev/null
    if [ `success` -ne 0 ]; then
        echo 1
    fi
    echo 0
}

function user_choice {
    local yn=
    read yn

    while true
    do
        case "$yn" in
            Y|y)
                echo 0
                break
            ;;
            *)
                echo 1
                break
            ;;
        esac
    done

}

function get_conda_build {
    _OK=`program_exists conda`
    if [ ! $_OK ]; then
        echo ''
    fi
    echo $( echo $( readlink -f $(dirname `which conda`)/../conda-bld ) )
}

function get_conda_repo {
    _OK=`program_exists conda`
    if [ ! $_OK ]; then
        echo "Cannot locate local conda repository."
        exit 1
    fi

    get_os_info
    echo "$(echo $(get_conda_build)/$OS-$ARCH)"
}

function get_os_info {
    OS=
    ARCH=
    _OS=`uname -s`
    _ARCH=`uname -m`

    case "$_OS" in
        Darwin)
            OS=osx
        ;;
        Linux)
            OS=linux
        ;;
        *)
            echo "Unsupported operating system"
            exit 1
        ;;
    esac

    case "$_ARCH" in
        i3*|i6*|x86)
            ARCH=32
        ;;
        x86_64)
            ARCH=64
        ;;
        *)
            echo "Unknown architecture"
            exit 1
        ;;
    esac

    export OS
    export ARCH
}
