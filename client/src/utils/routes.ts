export const getDashboardRoute = (role: string): string => {
  switch (role) {
    case 'ADMIN':
      return '/admin/dashboard'
    case 'PRODUCER':
      return '/producer/dashboard'
    case 'VERIFICATION_AUTHORITY':
      return '/authority/dashboard'
    case 'LAB':
      return '/lab/dashboard'
    case 'DISTRIBUTOR':
      return '/distributor/dashboard'
    default:
      return '/unauthorized'
  }
}
