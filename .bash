function _jira()
{
  latest="${COMP_WORDS[$COMP_CWORD]}"
  prev="${COMP_WORDS[$COMP_CWORD - 1]}"
  words=""
  e="a s d"
  case "${prev}" in
    jira)
      words="a g e d"
      ;;
    g)
      words="u t k"
      ;;
    d)
      words="u t"
      ;;
    a)
      words="'t' 'u'"
      ;;
    u)
      ;;
    t)
      ;;
    *)
      ;;
  esac
  COMPREPLY=($(compgen -W "$words" -- $latest))
  return 0
}

complete -F _jira jira
