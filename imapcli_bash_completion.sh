_imapcli()
{
  local cur

  COMPREPLY=()
  cur=${COMP_WORDS[COMP_CWORD]}

  COMPREPLY=( $( compgen -W '$(imapcli --help | grep imap-cli | cut -d" " -f6)' -- $cur ) )
}
complete -F _imapcli imapcli
