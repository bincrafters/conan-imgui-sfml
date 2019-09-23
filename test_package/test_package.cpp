#include "imgui.h"
#include "imgui-SFML.h"

#include <SFML/Graphics/RenderWindow.hpp>

int main() {
    sf::RenderWindow window;
    ImGui::SFML::Init(window);
    ImGui::SFML::Update(window, sf::Time());

    ImGui::Begin("Test window");
    ImGui::Text("Hello, World !");
    ImGui::End();

    ImGui::SFML::Shutdown();
    
    return 0;
}
