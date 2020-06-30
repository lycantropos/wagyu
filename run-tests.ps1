$compose_file = "docker-compose.yml"

docker-compose --build --exit-code-from wagyu

$STATUS = $LastExitCode

docker-compose down --remove-orphans

if ($STATUS -eq 0)
{
    echo "tests passed"
}
else
{
    echo "tests failed"
}

exit $STATUS
