import { redirect } from 'next/navigation'

export default function NewJobPage() {
    redirect('/admin/jobs?run=true')
}
