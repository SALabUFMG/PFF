#ifndef PLAYER_H
#define PLAYER_H

namespace football {
    class Player {
        public:
            int id;
            float position_x, position_y, velocity_x, velocity_y, vmax, reaction_time, tti_sigma, PPCF, time_to_intercept;
            Player();
            Player(int id, float position_x, float position_y, float velocity_x, float velocity_y, float vmax, float reaction_time, float tti_sigma);
            ~Player();
            float simple_time_to_intercept(float target_x, float target_y);
            float probability_intercept_ball(float t);
    };
}

#endif