#include "victim_localization/view_evaluator_ig_exp.h"

view_evaluator_ig_exp::view_evaluator_ig_exp():
  view_evaluator_base() //Call base class constructor
{
  ros::param::param<double>("~view_evaluator_weight_distance", w_dist_, 1.0);
}

double view_evaluator_ig_exp::calculateUtiltiy(geometry_msgs::Pose p, Victim_Map_Base *mapping_module, double &new_cell_percentage)
{
  double IG = calculateIG(p, mapping_module,new_cell_percentage);
  double dist = calculateDistance(p);
  return IG*exp(-dist*w_dist_);
}

double view_evaluator_ig_exp::calculateWirelessUtility(geometry_msgs::Pose p, Victim_Map_Base *mapping_module, double &new_cell_percentage)
{
  double IG = calculateWirelessIG(p,mapping_module,new_cell_percentage);
  double dist = calculateDistance(p);
  return IG*exp(-dist*w_dist_);
}

double view_evaluator_ig_exp::calculateCombinedUtility(geometry_msgs::Pose p,double &new_cell_percentage)
{
  double IG = view_evaluator_base::calculateCombinedUtility(p,new_cell_percentage);
  double dist = calculateDistance(p);

  return IG*exp(-dist*w_dist_);
}

std::string view_evaluator_ig_exp::getMethodName()
{
  return "IG_exp_" + std::to_string(w_dist_) +"_dist";
}


