#include <iostream>
#include <fstream>
using namespace std;

int main(int argc, char** argv) {

	ifstream traj("trajectories.txt", ios::in);
	if(!traj) return -1;


	string contenu;
	float a;

	getline(traj, contenu);

	cout << contenu << endl;

	traj >> a ;

	cout << a << endl;



	traj.close();

	return 0;
}