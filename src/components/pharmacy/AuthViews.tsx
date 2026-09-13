'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Cross, Loader2, LogIn, UserPlus } from 'lucide-react'
import { useLang } from './LangContext'
import { go } from '@/lib/router'
import { useToast } from '@/hooks/use-toast'

function AuthShell({ children, title, icon: Icon }: { children: React.ReactNode; title: string; icon: any }) {
  const { t } = useLang()
  return (
    <div className="max-w-md mx-auto px-4 py-14 w-full">
      <Card className="p-8 flex flex-col gap-6 shadow-xl shadow-primary/5 border-border/70">
        <div className="flex flex-col items-center gap-3 text-center">
          <span className="w-14 h-14 rounded-2xl bg-primary text-primary-foreground flex items-center justify-center shadow-lg shadow-primary/25">
            <Icon className="w-7 h-7" />
          </span>
          <h1 className="text-2xl font-black tracking-tight">{title}</h1>
          <span className="flex items-center gap-1.5 text-xs font-bold text-primary">
            <Cross className="w-3.5 h-3.5" /> {t('brand')}
          </span>
        </div>
        {children}
      </Card>
    </div>
  )
}

function ErrorMsg({ msg }: { msg: string }) {
  if (!msg) return null
  return <p className="text-sm font-semibold text-red-600 bg-red-50 border border-red-200 rounded-xl p-3 text-center">{msg}</p>
}

export function LoginView() {
  const { t, refreshUser, lang } = useLang()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error === 'invalid_credentials' ? t('invalid_credentials') : t('error_generic'))
        return
      }
      await refreshUser()
      toast({ description: `${t('welcome_back')}${data.user.name ? `, ${data.user.name}` : ''}` })
      go(data.user.isAdmin ? '/admin' : '/')
    } catch {
      setError(t('error_generic'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell title={t('welcome_back')} icon={LogIn}>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <ErrorMsg msg={error} />
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">{t('email')}</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required dir="ltr" className="rounded-xl h-11" placeholder="you@example.com" />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">{t('password')}</Label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required dir="ltr" className="rounded-xl h-11" placeholder="••••••••" />
        </div>
        <Button type="submit" size="lg" disabled={loading} className="rounded-2xl font-bold h-12 gap-2">
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <LogIn className="w-4 h-4" />} {t('login')}
        </Button>
      </form>
      <p className="text-sm text-muted-foreground text-center">
        {t('no_account')}{' '}
        <button onClick={() => go('/register')} className="font-bold text-primary hover:underline">{t('register')}</button>
      </p>
      <p className="text-[11px] text-muted-foreground/70 text-center font-mono bg-muted/50 rounded-xl p-2.5">{t('demo_hint')}</p>
    </AuthShell>
  )
}

export function RegisterView() {
  const { t, refreshUser } = useLang()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, phone, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        const map: Record<string, string> = {
          email_taken: t('email_taken'), weak_password: t('weak_password'), invalid_email: t('invalid_email'),
        }
        setError(map[data.error] || t('error_generic'))
        return
      }
      await refreshUser()
      go('/')
    } catch {
      setError(t('error_generic'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell title={t('create_account')} icon={UserPlus}>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <ErrorMsg msg={error} />
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">{t('name_optional')}</Label>
          <Input id="name" value={name} onChange={(e) => setName(e.target.value)} className="rounded-xl h-11" />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">{t('email')} *</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required dir="ltr" className="rounded-xl h-11" placeholder="you@example.com" />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="phone">{t('phone')}</Label>
          <Input id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} dir="ltr" className="rounded-xl h-11" placeholder="01012345678" />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">{t('password')} *</Label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required dir="ltr" className="rounded-xl h-11" placeholder="••••••••" minLength={6} />
        </div>
        <Button type="submit" size="lg" disabled={loading} className="rounded-2xl font-bold h-12 gap-2">
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <UserPlus className="w-4 h-4" />} {t('register')}
        </Button>
      </form>
      <p className="text-sm text-muted-foreground text-center">
        {t('have_account')}{' '}
        <button onClick={() => go('/login')} className="font-bold text-primary hover:underline">{t('login')}</button>
      </p>
    </AuthShell>
  )
}
