import React from 'react';
import { motion } from 'framer-motion';
import TaskOverview from '../components/TaskManagement/TaskOverview';
import TaskCalendar from '../components/TaskManagement/TaskCalendar';
import ResourceAllocation from '../components/TaskManagement/ResourceAllocation';
import TaskAnalytics from '../components/TaskManagement/TaskAnalytics';
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { PlusCircle } from 'lucide-react';

const TaskManagement = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-background"
    >
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Task Management</h1>
            <p className="text-muted-foreground mt-1">Manage and track your team's tasks efficiently</p>
          </div>
          <button className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg transition-colors">
            <PlusCircle size={20} />
            New Task
          </button>
        </div>

        <div className="bg-card rounded-xl shadow-sm border">
          <Tabs defaultValue="overview" className="w-full">
            <div className="border-b px-6 py-3">
              <TabsList className="inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground">
                <TabsTrigger value="overview" className="hover:text-foreground">
                  Overview
                </TabsTrigger>
                <TabsTrigger value="calendar" className="hover:text-foreground">
                  Calendar
                </TabsTrigger>
                <TabsTrigger value="resources" className="hover:text-foreground">
                  Resources
                </TabsTrigger>
                <TabsTrigger value="analytics" className="hover:text-foreground">
                  Analytics
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-6">
              <TabsContent value="overview" className="mt-0">
                <TaskOverview />
              </TabsContent>

              <TabsContent value="calendar" className="mt-0">
                <TaskCalendar />
              </TabsContent>

              <TabsContent value="resources" className="mt-0">
                <ResourceAllocation />
              </TabsContent>

              <TabsContent value="analytics" className="mt-0">
                <TaskAnalytics />
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    </motion.div>
  );
};

export default TaskManagement;
