# AWS Update Notification for Discord

## Parameter Store への Webhook の登録

事前に `/update-notification/target/webhooks/<channel_name>` に webhook の URL を入れておく必要がある。ただし、`/update-notification/target/webhooks/default` は必須。

※ Parameter の Prefix が決め打ちになっているので、そのうち直したい。

```bash
aws ssm put-parameter --type String --name /update-notification/target/webhooks/<channel_name> --value https://discord.com/api/webhooks/1234/ABCD
```

## Deploy

```bash
chalice deploy
```

## Invoke

```bash
cat test-event.json | chalice invoke -n check_news
```

## Delete

```bash
chalice delete
```

## Pipeline

```bash
aws secretsmanager create-secret --name GithubRepoAccess \
  --description "Token for Github Repo Access" \
  --secret-string '{"OAuthToken": "xxxxxxxx"}'

aws cloudformation deploy \
    --template-file pipeline.yml \
    --capabilities CAPABILITY_IAM \
    --stack-name {{ }} \
    --parameter-overrides \
        GithubOwner={{ }} \
        GithubRepoName={{  }}
```