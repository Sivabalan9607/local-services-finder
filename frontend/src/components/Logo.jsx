import logoSvg from '../assets/logo.svg'

export default function Logo({ className = '', height = 38 }) {
  return <img src={logoSvg} alt="Service Provider" className={className} style={{ height }} />
}
