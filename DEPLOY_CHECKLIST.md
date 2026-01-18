# Deployment Checklist

## Pre-Deployment

- [ ] Discord application created
- [ ] Bot token copied
- [ ] Client ID and secret copied
- [ ] Bot invited to test server
- [ ] Hosting account created
- [ ] GitHub repo ready (or code ready to upload)

## Services

- [ ] Postgres database added
- [ ] Redis added (optional)
- [ ] Bot service added
- [ ] Dashboard service added

## Environment Variables - Bot Service

- [ ] `DISCORD_TOKEN` set
- [ ] `DISCORD_CLIENT_ID` set
- [ ] `DISCORD_CLIENT_SECRET` set
- [ ] `DISCORD_REDIRECT_URI` set
- [ ] `DATABASE_URL` set
- [ ] `REDIS_URL` set
- [ ] `BASE_URL` set (bot public URL)
- [ ] `LOG_LEVEL=INFO` set

## Environment Variables - Dashboard Service

- [ ] `NEXT_PUBLIC_DISCORD_CLIENT_ID` set
- [ ] `DISCORD_CLIENT_SECRET` set
- [ ] `NEXT_PUBLIC_DISCORD_REDIRECT_URI` set
- [ ] `NEXT_PUBLIC_DASHBOARD_URL` set
- [ ] `DATABASE_URL` set
- [ ] `NEXTAUTH_URL` set
- [ ] `NEXTAUTH_SECRET` generated and set

## Post-Deployment

- [ ] Bot service deployed successfully
- [ ] Dashboard service deployed successfully
- [ ] Health check passes (`/health` endpoint)
- [ ] Bot responds to `/ping` in Discord
- [ ] `/setup` command works
- [ ] Dashboard accessible and OAuth works
- [ ] Discord redirect URI updated with production domain

## Testing

- [ ] Create ticket via `/ticket-panel`
- [ ] Create poll via `/poll-create`
- [ ] Set reminder via `/reminder-set`
- [ ] Create embed via `/embed-create`
- [ ] Check logs for errors

## Optional: Custom Domain

- [ ] Domain added
- [ ] DNS configured
- [ ] Environment variables updated with custom domain
- [ ] Services redeployed
- [ ] Discord redirect URI updated

---

**Ready to deploy?** Follow `DEPLOYMENT.md` for instructions.
