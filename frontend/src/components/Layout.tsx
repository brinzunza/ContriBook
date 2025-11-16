import { useState, useEffect } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { teamApi } from '../lib/api';
import { ChevronRight, ChevronDown } from 'lucide-react';

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedTeams, setExpandedTeams] = useState<Set<number>>(new Set());

  const { data: teams } = useQuery({
    queryKey: ['teams', 'active'],
    queryFn: async () => {
      const response = await teamApi.getMyTeams('active');
      return response.data;
    },
  });

  // Auto-expand team when viewing team or member page
  useEffect(() => {
    const teamMatch = location.pathname.match(/^\/teams\/(\d+)/);
    if (teamMatch && teams) {
      const teamId = parseInt(teamMatch[1]);
      if (!expandedTeams.has(teamId)) {
        setExpandedTeams(new Set([...expandedTeams, teamId]));
      }
    }
  }, [location.pathname, teams]);

  const toggleTeam = (teamId: number) => {
    const newExpanded = new Set(expandedTeams);
    if (newExpanded.has(teamId)) {
      newExpanded.delete(teamId);
    } else {
      newExpanded.add(teamId);
    }
    setExpandedTeams(newExpanded);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const isTeamActive = (teamId: number) => {
    return location.pathname.startsWith(`/teams/${teamId}`);
  };

  const isMemberActive = (teamId: number, memberId: number) => {
    return location.pathname === `/teams/${teamId}/members/${memberId}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col">
        <div className="p-4 border-b border-gray-100">
          <Link to="/dashboard" className="text-lg font-semibold text-gray-900">
            ContriBook
          </Link>
        </div>

        <nav className="flex-1 overflow-y-auto p-2">
          <Link
            to="/dashboard"
            className={`block px-2 py-1.5 rounded text-sm transition ${
              isActive('/dashboard') && !location.pathname.startsWith('/teams/')
                ? 'bg-gray-900 text-white'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            Dashboard
          </Link>

          <div className="mt-4">
            <div className="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wider">
              Teams
            </div>
            <div className="mt-1 space-y-0.5">
              {teams && teams.length > 0 ? (
                teams.map((team) => {
                  const isExpanded = expandedTeams.has(team.id);
                  const teamIsActive = isTeamActive(team.id);
                  
                  return (
                    <TeamDirectoryItem
                      key={team.id}
                      team={team}
                      isExpanded={isExpanded}
                      isActive={teamIsActive}
                      onToggle={() => toggleTeam(team.id)}
                      isMemberActive={isMemberActive}
                    />
                  );
                })
              ) : (
                <div className="px-2 py-1 text-xs text-gray-500">No teams</div>
              )}
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="mb-3">
            <div className="text-xs text-gray-500 mb-1">Signed in as</div>
            <div className="text-sm font-medium text-gray-900">{user?.username}</div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left px-2 py-1.5 rounded text-sm text-gray-600 hover:bg-gray-50"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

interface TeamDirectoryItemProps {
  team: { id: number; name: string };
  isExpanded: boolean;
  isActive: boolean;
  onToggle: () => void;
  isMemberActive: (teamId: number, memberId: number) => boolean;
}

function TeamDirectoryItem({ team, isExpanded, isActive, onToggle, isMemberActive }: TeamDirectoryItemProps) {
  const { data: members } = useQuery({
    queryKey: ['team-members', team.id],
    queryFn: async () => {
      const response = await teamApi.getTeamMembers(team.id);
      return response.data;
    },
    enabled: isExpanded,
  });

  return (
    <div>
      <div
        className={`flex items-center px-2 py-1.5 rounded text-sm cursor-pointer transition ${
          isActive
            ? 'bg-gray-900 text-white'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
        onClick={(e) => {
          e.preventDefault();
          onToggle();
        }}
      >
        <span className="mr-1.5">
          {isExpanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
        </span>
        <Link
          to={`/teams/${team.id}`}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 truncate"
        >
          {team.name}
        </Link>
      </div>
      {isExpanded && members && (
        <div className="ml-4 mt-0.5 space-y-0.5">
          {members.map((member) => {
            const memberActive = isMemberActive(team.id, member.id);
            return (
              <Link
                key={member.id}
                to={`/teams/${team.id}/members/${member.id}`}
                className={`block px-2 py-1.5 rounded text-sm transition ${
                  memberActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {member.full_name || member.username}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
