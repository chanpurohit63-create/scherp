// Backward compatibility wrapper - uses SchoolAdminLayout
import SchoolAdminLayout from './SchoolAdminLayout'
export default function PageWrapper(props) {
  return <SchoolAdminLayout {...props} />
}