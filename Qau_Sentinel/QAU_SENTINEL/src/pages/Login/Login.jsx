import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Eye, EyeOff, LogIn, Shield, Camera } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      console.error("Login error:", err);
      setError(err.response?.data?.error || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0B1220] px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-blue-600">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-white">QAU Sentinel</h1>
              <p className="text-sm text-slate-400">AI Surveillance Platform</p>
            </div>
          </div>
          <h2 className="text-xl font-semibold text-white">Welcome Back</h2>
          <p className="text-sm text-slate-400 mt-1">Sign in to access the dashboard</p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error */}
            {error && (
              <div className="rounded-lg bg-red-600/20 border border-red-600/30 p-3 text-sm text-red-400">
                {error}
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@qau.edu.pk"
                required
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 pr-12 text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
                <input type="checkbox" className="h-4 w-4 rounded border-slate-700 bg-slate-950" />
                Remember me
              </label>
              <button
                type="button"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot password?
              </button>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? (
                <>
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Sign In
                </>
              )}
            </button>

            {/* Demo Credentials */}
            {import.meta.env.DEV && (
              <div className="border-t border-slate-800 pt-4 mt-2">
                <p className="text-center text-xs text-slate-500 mb-3">Demo Credentials</p>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-center">
                    <p className="text-slate-500">Admin</p>
                    <p className="text-white font-mono text-[10px] truncate">admin@qau.edu.pk</p>
                    <p className="text-slate-500 font-mono text-[10px]">admin123</p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-center">
                    <p className="text-slate-500">Operator</p>
                    <p className="text-white font-mono text-[10px] truncate">operator1@qau.edu.pk</p>
                    <p className="text-slate-500 font-mono text-[10px]">operator123</p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-center">
                    <p className="text-slate-500">Viewer</p>
                    <p className="text-white font-mono text-[10px] truncate">viewer1@qau.edu.pk</p>
                    <p className="text-slate-500 font-mono text-[10px]">viewer123</p>
                  </div>
                </div>
              </div>
            )}

            {/* form end */}
          </form>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-xs text-slate-500">
            QAU Sentinel v1.0.0 • AI Safety & Anomaly Detection Platform
          </p>
        </div>
      </div>
    </div>
  );
}
