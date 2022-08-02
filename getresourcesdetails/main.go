package main

import (
	"log"
	"fmt"
	"context"
	// "github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"github.com/hashicorp/terraform-provider-aws/internal/provider"
)

func main() {
	providers, err := provider.New(context.Background())

	if err != nil {
		log.Fatal(err)
	}
	for resource_name, resource := range providers.ResourcesMap {
		fmt.Println("On parcourt ", resource_name)
		// for i, j := range resource.Schema {
		// 	fmt.Println("Champ",i,"= ", j)
		// }

		fmt.Println("***** Input variables *****")
		for i, j := range resource.Schema {
			// Traiter le champs Elem
			fmt.Printf("Champ %s. type = %s ; required = %t ; optional = %t ; computed = %t ; forceNew = %t; deprecated = %+v ; sensitive = %t \n", i,j.Type, j.Required, j.Optional, j.Computed, j.ForceNew, j.Deprecated, j.Sensitive)
		}
		fmt.Println("***** Description *****")
		fmt.Printf("%s\n", resource.Description)
		fmt.Println("***** Read function *****")
		fmt.Println("***** Output variables *****")
    }
}
