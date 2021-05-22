# AWS Update Notification

## Parameter Store への Webhook の登録

```bash
aws ssm put-parameter --type String --name /startup-community/discord/webhooks/<channel_name> --value https://discord.com/api/webhooks/1234/ABCD
```

## Deploy

```bash
chalice deploy

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
    --template-file pipeline.json \
    --capabilities CAPABILITY_IAM \
    --stack-name {{ }} \
    --parameter-overrides \
        GithubOwner={{ }} \
        GithubRepoName={{  }} \
```