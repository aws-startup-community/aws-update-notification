# AWS Update Notification

## Parameter Store への Webhook の登録

```bash
aws ssm put-parameter --type String --name /startup-community/discord/webhooks/<channel_name> --value https://discord.com/api/webhooks/1234/ABCD
```

## Deploy

```bash
chalice deploy [--stage prod] [--profile prod]
```

## Invoke

```bash
cat test-event.json | chalice invoke -n check_news [--stage prod] [--profile prod]
```

## Delete

```bash
chalice delete [--stage prod] [--profile prod]
```