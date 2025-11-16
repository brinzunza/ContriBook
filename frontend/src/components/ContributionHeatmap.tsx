import { useMemo } from 'react';
import type { Contribution } from '../types';

interface ContributionHeatmapProps {
  contributions: Contribution[];
}

interface DayData {
  date: Date;
  count: number;
  level: number;
}

export function ContributionHeatmap({ contributions }: ContributionHeatmapProps) {
  const heatmapData = useMemo(() => {
    // Get date 365 days ago
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 364); // 365 days including today

    // Create a map of date strings to contribution counts
    const contributionsByDate = new Map<string, number>();

    contributions.forEach((contribution) => {
      const date = new Date(contribution.created_at);
      const dateStr = date.toISOString().split('T')[0];
      contributionsByDate.set(dateStr, (contributionsByDate.get(dateStr) || 0) + 1);
    });

    // Find max contributions in a single day for level calculation
    const maxCount = Math.max(...Array.from(contributionsByDate.values()), 1);

    // Generate data for all days
    const days: DayData[] = [];
    const currentDate = new Date(startDate);

    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      const count = contributionsByDate.get(dateStr) || 0;

      // Calculate level (0-4) like GitHub
      let level = 0;
      if (count > 0) {
        const percentage = count / maxCount;
        if (percentage >= 0.75) level = 4;
        else if (percentage >= 0.5) level = 3;
        else if (percentage >= 0.25) level = 2;
        else level = 1;
      }

      days.push({
        date: new Date(currentDate),
        count,
        level,
      });

      currentDate.setDate(currentDate.getDate() + 1);
    }

    return days;
  }, [contributions]);

  // Group days by week
  const weeks = useMemo(() => {
    const result: DayData[][] = [];
    let week: DayData[] = [];

    // Add empty cells for the first week to align with Sunday
    const firstDay = heatmapData[0];
    if (firstDay) {
      const dayOfWeek = firstDay.date.getDay();
      for (let i = 0; i < dayOfWeek; i++) {
        week.push({ date: new Date(0), count: 0, level: -1 }); // Empty cell
      }
    }

    heatmapData.forEach((day, index) => {
      week.push(day);

      // Sunday (0) or last day
      if (day.date.getDay() === 6 || index === heatmapData.length - 1) {
        result.push([...week]);
        week = [];
      }
    });

    return result;
  }, [heatmapData]);

  const getColor = (level: number) => {
    if (level === -1) return 'transparent'; // Empty cell
    if (level === 0) return '#ebedf0'; // No contributions
    if (level === 1) return '#9be9a8'; // Low
    if (level === 2) return '#40c463'; // Medium-low
    if (level === 3) return '#30a14e'; // Medium-high
    return '#216e39'; // High
  };

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Calculate which months to show labels for
  const monthLabels = useMemo(() => {
    const labels: { month: string; column: number }[] = [];
    let lastMonth = -1;

    weeks.forEach((week, weekIndex) => {
      const firstValidDay = week.find(d => d.level !== -1);
      if (firstValidDay) {
        const month = firstValidDay.date.getMonth();
        if (month !== lastMonth) {
          labels.push({ month: months[month], column: weekIndex });
          lastMonth = month;
        }
      }
    });

    return labels;
  }, [weeks]);

  const totalContributions = useMemo(() => {
    return heatmapData.reduce((sum, day) => sum + day.count, 0);
  }, [heatmapData]);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Contribution Activity</h3>
        <p className="text-sm text-gray-600 mt-1">
          {totalContributions} contributions in the last year
        </p>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="flex">
            {/* Day labels spacer */}
            <div style={{ width: '32px' }} />

            {/* Month labels */}
            <div className="flex mb-2 relative" style={{ height: '20px' }}>
              {monthLabels.map((label, index) => (
                <div
                  key={index}
                  className="text-xs text-gray-600 absolute"
                  style={{
                    left: `${label.column * 13}px`,
                  }}
                >
                  {label.month}
                </div>
              ))}
            </div>
          </div>

          <div className="flex">
            {/* Day labels */}
            <div className="flex flex-col justify-around pr-2" style={{ width: '32px', height: `${7 * 11}px` }}>
              <div className="text-xs text-gray-600" style={{ lineHeight: '10px' }}>Mon</div>
              <div className="text-xs text-gray-600" style={{ lineHeight: '10px' }}>Wed</div>
              <div className="text-xs text-gray-600" style={{ lineHeight: '10px' }}>Fri</div>
            </div>

            {/* Heatmap grid */}
            <div className="flex gap-1">
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-1">
                  {week.map((day, dayIndex) => {
                    const dateStr = day.level !== -1
                      ? day.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                      : '';
                    const tooltip = day.level !== -1
                      ? `${day.count} contribution${day.count !== 1 ? 's' : ''} on ${dateStr}`
                      : '';

                    return (
                      <div
                        key={dayIndex}
                        className="rounded-sm"
                        style={{
                          width: '10px',
                          height: '10px',
                          backgroundColor: getColor(day.level),
                          border: day.level === -1 ? 'none' : '1px solid rgba(27,31,35,0.06)',
                        }}
                        title={tooltip}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-end mt-4 text-xs text-gray-600 gap-2">
            <span>Less</span>
            {[0, 1, 2, 3, 4].map((level) => (
              <div
                key={level}
                className="rounded-sm"
                style={{
                  width: '10px',
                  height: '10px',
                  backgroundColor: getColor(level),
                  border: '1px solid rgba(27,31,35,0.06)',
                }}
              />
            ))}
            <span>More</span>
          </div>
        </div>
      </div>
    </div>
  );
}
