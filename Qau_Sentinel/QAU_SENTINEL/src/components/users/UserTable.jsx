import { Edit, Trash2, User, CheckCircle, XCircle } from "lucide-react";

const ROLE_COLORS = {
  Admin: "bg-purple-600/20 text-purple-400 border-purple-600/30",
  Operator: "bg-blue-600/20 text-blue-400 border-blue-600/30",
  Viewer: "bg-slate-600/20 text-slate-400 border-slate-600/30",
};

export default function UserTable({ users, onEdit, onDelete }) {
  if (!users || users.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 py-16 text-center">
        <p className="text-slate-400">No users found matching your criteria.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
      <div className="overflow-x-auto">
        <table className="w-full min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
                User
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
                Email
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
                Role
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
                Status
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium uppercase tracking-wider text-slate-400">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-slate-800/50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800">
                      <User className="h-4 w-4 text-slate-400" />
                    </div>
                    <span className="font-medium text-white">{user.username}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-400">
                  {user.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${ROLE_COLORS[user.role] || ROLE_COLORS.Viewer}`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {user.is_active ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                        <span className="text-emerald-400 text-sm">Active</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-4 w-4 text-red-400" />
                        <span className="text-red-400 text-sm">Inactive</span>
                      </>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onEdit(user)}
                      className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDelete(user)}
                      className="rounded-lg p-2 text-slate-400 hover:bg-red-600/20 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}